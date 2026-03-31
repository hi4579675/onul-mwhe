package com.onulmwhe.user.security;

import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.oauth2.core.user.OAuth2User;

import java.util.Collection;
import java.util.Map;

/**
 * Spring Security의 OAuth2User를 래핑해 userId를 직접 노출.
 *
 * OAuth2LoginSuccessHandler에서 authentication.getPrincipal()을 이 타입으로 캐스팅해
 * getUserId()를 바로 호출할 수 있음. 프로바이더별 attribute map을 다시 파싱할 필요 없음.
 *
 * getName() → userId를 반환하므로 SecurityContextHolder의 principal name이
 * JWT subject와 동일한 포맷("kakao_123456789")이 됨.
 */
public class CustomOAuth2User implements OAuth2User{
    private final OAuth2User delegate;
    private final String userId;

    public CustomOAuth2User(OAuth2User delegate, String userId) {
        this.delegate = delegate;
        this.userId = userId;
    }
    /** JWT subject, routes.user_id, favorite_places.user_id와 동일한 값 */
    public String getUserId() {
        return userId;
    }
    @Override
    public Map<String, Object> getAttributes() {
        return delegate.getAttributes();
    }

    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        return delegate.getAuthorities();
    }

    /** principal name = userId → SecurityContext에서 authentication.getName()으로 접근 가능 */
    @Override
    public String getName() {
        return userId;
    }
}
