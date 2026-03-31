package com.onulmwhe.user.security;

import com.onulmwhe.user.entity.User;
import com.onulmwhe.user.repository.UserRepository;
import com.onulmwhe.user.security.oauth2.OAuth2UserInfo;
import com.onulmwhe.user.security.oauth2.OAuth2UserInfoFactory;
import lombok.RequiredArgsConstructor;
import org.springframework.security.oauth2.client.userinfo.DefaultOAuth2UserService;
import org.springframework.security.oauth2.client.userinfo.OAuth2UserRequest;
import org.springframework.security.oauth2.core.OAuth2AuthenticationException;
import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class CustomOAuth2UserService extends DefaultOAuth2UserService {

    private final UserRepository userRepository;

    @Override
    @Transactional
    public OAuth2User loadUser(OAuth2UserRequest userRequest) throws OAuth2AuthenticationException {
        // 1. Spring 기본 구현으로 kakao user - info endpoint 호출 및 속성 추천
        OAuth2User oAuth2User = super.loadUser(userRequest);

        // 2. 프로바이더 식별 ("kakao" → application.yml의 registration 키와 일치)
        String registrationId = userRequest
            .getClientRegistration()
            .getRegistrationId();

        // 3. 프로바이더별 중첩 구조를 OAuthUserInfo 인터페이스로 추상화
        OAuth2UserInfo userInfo = OAuth2UserInfoFactory.of(
            registrationId,
            oAuth2User.getAttributes()
        );

        // 4. DB upsert : 이미 가입된 사용자면 프로필 갱신, 신규면 INSERT
        User user = userRepository
            .findByProviderAndProviderId(userInfo.getProvider(), userInfo.getProviderId())
            .map(existing -> {
                // 매 로그인마다 닉네임/이메일 최신화
                existing.updateProfile(userInfo.getEmail(), userInfo.getNickname());
                return existing;
            })
            .orElseGet(() -> userRepository.save(
                User.of(
                    userInfo.getProvider(),
                    userInfo.getProviderId(),
                    userInfo.getEmail(),
                    userInfo.getNickname()
                )
            ));
        // 5. successHandler에서 getUserId()로 JWT subject를 즉시 가져올 수 있도록
        return new CustomOAuth2User(oAuth2User, user.getUserId());
    }
}
