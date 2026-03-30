package com.onulmwhe.backend.config;

import com.onulmwhe.backend.security.OAuth2LoginFailureHandler;
import com.onulmwhe.backend.security.OAuth2LoginSuccessHandler;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
public class SecurityConfig {

    @Bean
    public SecurityFilterChain securityFilterChain(
        HttpSecurity http,
        OAuth2LoginSuccessHandler successHandler,
        OAuth2LoginFailureHandler failureHandler
    ) throws Exception {
        http
            .csrf(csrf -> csrf.disable())
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/actuator/health", "/error", "/api/v1/routes/**", "/api/v1/places/**").permitAll()
                .anyRequest().authenticated()
            )
            .oauth2Login(oauth2 -> oauth2
                .successHandler(successHandler)
                .failureHandler(failureHandler)
            )
            .httpBasic(Customizer.withDefaults());

        return http.build();
    }
}
