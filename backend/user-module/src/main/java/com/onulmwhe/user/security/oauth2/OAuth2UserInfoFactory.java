package com.onulmwhe.user.security.oauth2;

import java.util.Map;

/**
 * registrationId("kakao" / "google" / "naver")를 받아
 * 맞는 OAuth2UserInfo 구현체를 반환하는 정적 팩토리.
 *
 * 새 프로바이더 추가 시:
 *   1. application.yml에 registration/provider 추가
 *   2. XxxOAuth2UserInfo 구현체 작성
 *   3. 여기에 case 한 줄 추가
 *   <- CustomOAuth2UserService, User 등 다른 클래스 변경 없음
 */
public final class OAuth2UserInfoFactory {

    private OAuth2UserInfoFactory() {}

    public static OAuth2UserInfo of(String registrationId, Map<String, Object> attributes) {
        return switch (registrationId.toLowerCase()) {
            case "kakao"  -> new KakaoOAuth2UserInfo(attributes);
            // case "google" -> new GoogleOAuth2UserInfo(attributes);
            // case "naver"  -> new NaverOAuth2UserInfo(attributes);
            default -> throw new IllegalArgumentException(
                "지원하지 않는 OAuth2 프로바이더: " + registrationId
            );
        };
    }
}
