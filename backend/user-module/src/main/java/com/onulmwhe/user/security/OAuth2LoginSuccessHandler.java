package com.onulmwhe.user.security;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;

import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.core.Authentication;
import org.springframework.security.web.authentication.AuthenticationSuccessHandler;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
public class OAuth2LoginSuccessHandler implements AuthenticationSuccessHandler {

    private final JwtProvider jwtProvider;

    @Value("${app.oauth2.success-redirect:http://localhost:3000/oauth/callback}")
    private String successRedirect;

    @Override
    public void onAuthenticationSuccess(
        HttpServletRequest request,
        HttpServletResponse response,
        Authentication authentication)
        throws IOException, ServletException {

        /*
         * SecurityConfig에서 CustomOAuth2UserService를 userService로 등록했으므로
         * getPrincipal()은 항상 CustomOAuth2User 타입.
         * getUserId()는 "kakao_123456789" 포맷 → JWT subject로 사용.
         */
        CustomOAuth2User oAuth2User = (CustomOAuth2User) authentication.getPrincipal();
        String token = jwtProvider.generateToken(oAuth2User.getUserId());

        /*
         * React SPA는 /oauth/callback 페이지에서 window.location.search의
         * ?token= 값을 읽어 localStorage 등에 저장 후 API 호출에 사용.
         *
         * 향후 HttpOnly Secure Cookie로 교체 시 이 핸들러만 수정하면 됨:
         *   Cookie c = new Cookie("access_token", token);
         *   c.setHttpOnly(true); c.setSecure(true); c.setPath("/");
         *   response.addCookie(c);
         *   response.sendRedirect(successRedirect);
         */
        response.sendRedirect(successRedirect + "?token=" + URLEncoder.encode(token, StandardCharsets.UTF_8));
    }

}
