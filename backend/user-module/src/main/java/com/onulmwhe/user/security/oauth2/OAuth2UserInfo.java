package com.onulmwhe.user.security.oauth2;

/**
 * OAuth2 프로바이더별 응답 구조 차이를 추상화하는 인터페이스.
 *
 * 카카오:  { id: 123, properties: { nickname }, kakao_account: { email } }
 * 구글:    { sub: "abc", name: "...", email: "..." }
 * 네이버:  { resultcode: "00", response: { id, name, email } }
 *
 * CustomOAuth2UserService는 이 인터페이스만 참조하므로
 * 새 프로바이더 추가 시 CustomOAuth2UserService 수정 불필요.
 */
public interface OAuth2UserInfo {
    /** 소문자 프로바이더명. 예: "kakao" */
    String getProvider();

    /**
     * 프로바이더가 부여한 고유 ID.
     * User.userId = getProvider() + "_" + getProviderId() 로 조합됨.
     */
    String getProviderId();

    /** 이메일 스코프 거부 시 null 가능 */
    String getEmail();

    String getNickname();
}
