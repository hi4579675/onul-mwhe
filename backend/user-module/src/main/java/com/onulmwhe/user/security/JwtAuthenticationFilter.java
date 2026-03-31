package com.onulmwhe.user.security;



import com.fasterxml.jackson.databind.ObjectMapper;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.ExpiredJwtException;
import io.jsonwebtoken.JwtException;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.List;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.MediaType;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.filter.OncePerRequestFilter;
/**
 * @Component 없음 — 의도적 설계.
 * Spring Boot는 Filter 구현체에 @Component가 있으면
 * FilterRegistrationBean으로 Servlet 체인에 자동 등록함.
 * SecurityConfig에서 .addFilterBefore()로 Security 체인에도 등록하면
 * 동일 요청에 이 필터가 2번 실행됨.
 * @Component 없이 SecurityConfig에서만 등록 → 단 1회 실행 보장.
 */
public class JwtAuthenticationFilter extends OncePerRequestFilter {
    private static final Logger log = LoggerFactory.getLogger(JwtAuthenticationFilter.class);

    private final JwtProvider jwtProvider;
    private final ObjectMapper objectMapper;

    public JwtAuthenticationFilter(JwtProvider jwtProvider,  ObjectMapper objectMapper) {
        this.jwtProvider = jwtProvider;
        this.objectMapper = objectMapper;
    }
    /**
     * 처리 흐름:
     * 1. Authorization 헤더 → 토큰 추출 (없으면 통과 — OAuth2/public 경로 대응)
     * 2. extractClaims() 로 서명 검증 + Claims 파싱 (1회)
     *    - ExpiredJwtException → 401 + TOKEN_EXPIRED
     *    - JwtException        → 401 + TOKEN_INVALID
     * 3. subject(userId) 꺼내 SecurityContext 등록
     *    → 컨트롤러에서 @AuthenticationPrincipal String userId 로 주입
     */
    @Override
    protected void doFilterInternal(
        HttpServletRequest request,
        HttpServletResponse response,
        FilterChain filterChain) throws ServletException, IOException {

        // 1. 헤더 -> 토큰 추출 ( resolveToken은 JwtProvider 책임)
        String token = jwtProvider.resolveToken(
            request.getHeader(JwtProvider.AUTHORIZATION_HEADER)
        );

        // 토큰 없음 -> 인증 없이 다음 필터로
        if (token == null) {
            filterChain.doFilter(request, response);
        }
        // 2. 검증 + 파싱
        Claims claims;
        try {
            claims = jwtProvider.extractClaims(token);
        } catch (ExpiredJwtException e ) {
            // 만료 토큰 : 프론트에서 재로그인 유도
            log.debug("[JWT] 만료된 토큰: {}", e.getMessage());
            sendError(response, HttpServletResponse.SC_UNAUTHORIZED, "TOKEN_EXPIRED", "토큰이 만료되었습니다.");
            return;
        } catch (JwtException | IllegalArgumentException e) {
            // 변조·형식 오류: 재로그인 필요
            log.warn("[JWT] 유효하지 않은 토큰: {}", e.getMessage());
            sendError(response, HttpServletResponse.SC_UNAUTHORIZED, "TOKEN_INVALID", "유효하지 않은 토큰입니다.");
            return;
        }
        // 3. subject = "kakao_123456789" → SecurityContext 등록
        String userId = claims.getSubject();

        /*
         * 3인자 생성자 — authenticated = true.
         * 2인자 생성자는 authenticated = false → Security가 다시 인증 시도.
         * principal에 userId(String)를 넣으면 컨트롤러에서
         * @AuthenticationPrincipal String userId 로 바로 꺼낼 수 있음.
         */
        UsernamePasswordAuthenticationToken authentication =
            new UsernamePasswordAuthenticationToken(
                userId,
                null,
                List.of(new SimpleGrantedAuthority("ROLE_USER"))
            );

        SecurityContextHolder.getContext().setAuthentication(authentication);
        filterChain.doFilter(request, response);
    }

    /**
     * 401 JSON 응답 전송.
     *
     * 별도 JwtExceptionFilter 없이 필터 안에서 직접 응답하는 이유:
     * JwtExceptionFilter를 추가하면 필터 순서 관리가 복잡해지고
     * GlobalExceptionHandler와 역할이 겹침.
     * JWT 오류는 인증 단계 문제이므로 이 필터에서 바로 처리하는 게 명확함.
     */
    private void sendError(
        HttpServletResponse response,
        int status,
        String code,
        String message
    ) throws IOException {
        response.setStatus(status);
        response.setContentType(MediaType.APPLICATION_JSON_VALUE);
        response.setCharacterEncoding("UTF-8");
        response.getWriter().write(
            objectMapper.writeValueAsString(Map.of("code", code, "message", message))
        );
    }
}
