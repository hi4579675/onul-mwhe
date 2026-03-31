package com.onulmwhe.user.security;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.io.Decoders;
import io.jsonwebtoken.security.Keys;
import lombok.AllArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.util.Date;

@Component
public class JwtProvider {
    private static final Logger log = LoggerFactory.getLogger(JwtProvider.class);

    public static final String AUTHORIZATION_HEADER = "Authorization";
    public static final String BEARER_PREFIX = "Bearer ";

    private final SecretKey key;
    private final long expirationMs;

    /**
     * 생성자 주입 방식 사용 이유:
     * @PostConstruct 방식은 의존성 주입 완료 후 별도 초기화 단계가 필요하지만,
     * 생성자 주입은 빈 생성 시점에 key가 바로 완성되어 불변 객체로 만들 수 있음.
     * 단위 테스트 시 new JwtProvider("secret", 3600000L) 형태로 바로 생성 가능.
     *
     * JWT_SECRET은 Base64 인코딩된 최소 32바이트 문자열.
     * 생성: openssl rand -base64 32
     */
    public JwtProvider(
        @Value("${jwt.secret}") String base64Secret,
        @Value("${jwt.expiration-ms}") long expirationMs
    ) {
        this.key = Keys.hmacShaKeyFor(Decoders.BASE64.decode(base64Secret));
        this.expirationMs = expirationMs;
    }

    // ─── 토큰 생성 ────────────────────────────────────────────────────────────
    /**
     * JWT 발급.
     *
     * subject = "{provider}_{providerId}" (예: "kakao_123456789")
     * routes.user_id / favorite_places.user_id와 동일한 포맷이어야
     * 기존 데이터와 매핑되고 DB 마이그레이션이 필요 없음.
     */
    public String generateToken(String subject) {
        Date now = new Date();
        Date expiry =  new Date(now.getTime() + expirationMs);

        return Jwts.builder()
            .subject(subject)
            .issuedAt(now)
            .expiration(expiry)
            .signWith(key)
            .compact();
    }
// ── 토큰 파싱 ──────────────────────────────────────────────────────────────

    /**
     * 토큰 검증 + Claims 추출을 한 번에 처리.
     *
     * validateToken() + getSubject()를 분리하면 파싱이 2번 일어남.
     * 이 메서드 하나로 파싱 1회 → 성능·가독성 모두 개선.
     *
     * 예외를 삼키지 않고 그대로 throw하는 이유:
     * 만료(ExpiredJwtException)와 변조(JwtException)를 호출부(필터)에서 구분해
     * 다른 에러 메시지/코드로 응답할 수 있게 하기 위함.
     * 여기서 catch하면 필터가 구분 불가.
     * @throws ExpiredJwtException  토큰 만료
     * @throws JwtException         서명 불일치, 형식 오류 등
     */
    public Claims extractClaims(String token) {
        return Jwts.parser()
            .verifyWith(key)
            .build()
            .parseSignedClaims(token)
            .getPayload();
    }

    // ── 토큰 유틸 ──────────────────────────────────────────────────────────────
    /**
     * Authorization 헤더 → 순수 토큰 추출.
     * "Bearer eyJ..." → "eyJ..."
     *
     * JwtProvider에 위치시키는 이유 (SRP):
     * 필터가 헤더 파싱 방식을 알 필요 없음.
     * Bearer 접두사 규칙이 바뀌어도 이 메서드만 수정하면 됨.
     *
     * @return 순수 토큰 문자열. 헤더가 없거나 Bearer 형식이 아니면 null.
     */
    public String resolveToken(String bearerToken) {
        if (bearerToken != null && bearerToken.startsWith(BEARER_PREFIX)) {
            return bearerToken.substring(BEARER_PREFIX.length());
        }
        return null;
    }
    /**
     * 토큰 남은 유효 시간 반환 (밀리초).
     * 향후 로그아웃 시 Redis 블랙리스트 TTL 설정에 사용.
     * (access token 남은 시간만큼만 블랙리스트 유지하면 됨)
     */
    public long getExpiration(String token) {
        return extractClaims(token).getExpiration().getTime() - new Date().getTime();
    }
}
