package com.onulmwhe.user.security.oauth2;

import java.util.Map;

public class KakaoOAuth2UserInfo implements OAuth2UserInfo {
    private final Map<String, Object> attributes;
    public KakaoOAuth2UserInfo(Map<String, Object> attributes) {
        this.attributes = attributes;
    }
    @Override
    public String getProvider() {
        return "kakao";
    }

    @Override
    public String getProviderId() {
        // Kakao는 id를 Long으로 반환. String.valueOf로 안전하게 변환.
        return String.valueOf(attributes.get("id"));
    }

    @Override
    public String getEmail() {
        // kakao_account 자체가 없을 수 있음 (스코프 미동의)
        Object kakaoAccount = attributes.get("kakao_account");
        if (kakaoAccount instanceof Map<?, ?> accountMap) {
            Object email = accountMap.get("email");
            return email != null ? (String) email : null;
        }
        return null;
    }

    @Override
    public String getNickname() {
        // properties.nickname이 가장 안정적인 소스
        Object properties = attributes.get("properties");
        if (properties instanceof Map<?, ?> propsMap) {
            Object nickname = propsMap.get("nickname");
            return nickname != null ? (String) nickname : null;
        }
        return null;
    }
}

