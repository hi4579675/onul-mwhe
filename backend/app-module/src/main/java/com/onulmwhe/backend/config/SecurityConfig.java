package com.onulmwhe.backend.config;

import com.onulmwhe.backend.security.OAuth2LoginFailureHandler;
import com.onulmwhe.backend.security.OAuth2LoginSuccessHandler;
import com.onulmwhe.user.security.CustomOAuth2UserService;
import com.onulmwhe.user.security.JwtAuthenticationFilter;
import com.onulmwhe.user.security.JwtProvider;
import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

@Configuration
@RequiredArgsConstructor
public class SecurityConfig {

    private final CustomOAuth2UserService  customOAuth2UserService;
    private final OAuth2LoginSuccessHandler successHandler;
    private final OAuth2LoginFailureHandler failureHandler;
    private final JwtProvider jwtProvider;

    /**
     * JwtAuthenticationFilter를 @Bean으로 등록하는 이유:
     * - @Component 없이 Security 체인에서만 단일 실행되도록 하기 위함.
     * - @Configuration 클래스의 @Bean 메서드는 Spring DI에 참여하므로
     *   JwtProvider가 정상적으로 주입됨.
     */
    @Bean
    public JwtAuthenticationFilter jwtAuthenticationFilter() {
        return new JwtAuthenticationFilter(jwtProvider);
    }

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())

            /*
             * IF_REQUIRED를 사용하는 이유:
             * OAuth2 인가코드 플로우는 CSRF 방지용 state 파라미터를 HttpSession에 저장.
             * STATELESS로 설정하면 Kakao 리다이렉트 콜백 시 세션이 없어
             * "authorization_request_not_found" 예외가 발생함.
             * IF_REQUIRED는 OAuth2 플로우에서만 세션을 생성하고,
             * JWT로 인증된 API 요청은 세션을 건드리지 않아 사실상 stateless하게 동작.
             */
            .sessionManagement(session ->
                session.sessionCreationPolicy(SessionCreationPolicy.IF_REQUIRED)
            )

            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/actuator/health", "/error").permitAll()
                /*
                 * routes/places를 authenticated()로 변경하는 이유:
                 * userId가 JWT에서 오므로 인증 없는 요청은 principal이 없어 동작 불가.
                 * 명시적으로 authenticated()를 지정해야 401이 깔끔하게 반환됨.
                 * (기존 permitAll()은 X-User-Id 헤더 방식일 때의 임시 설정이었음)
                 */
                .requestMatchers("/api/v1/routes/**", "/api/v1/places/**").authenticated()
                .anyRequest().authenticated()
            )

            /*
             * JWT 필터를 UsernamePasswordAuthenticationFilter 앞에 배치.
             * 유효한 Bearer 토큰이 있으면 여기서 SecurityContext가 채워져
             * 이후 필터들이 추가 인증을 시도하지 않음.
             * 토큰이 없으면 (OAuth2 리다이렉트 등) 그냥 통과해 OAuth2 흐름 계속.
             */
            .addFilterBefore(jwtAuthenticationFilter(), UsernamePasswordAuthenticationFilter.class)

            .oauth2Login(oauth2 -> oauth2
                /*
                 * CustomOAuth2UserService를 등록해야 principal이 CustomOAuth2User가 됨.
                 * 등록하지 않으면 기본 DefaultOAuth2UserService가 사용되어
                 * SuccessHandler의 (CustomOAuth2User) 캐스팅이 실패함.
                 */
                .userInfoEndpoint(userInfo ->
                    userInfo.userService(customOAuth2UserService)
                )
                .successHandler(successHandler)
                .failureHandler(failureHandler)
            );
        // httpBasic 제거: 이 앱에서 Basic 인증 사용처 없음. 불필요한 공격 면적 제거.
        return http.build();
    }
}
