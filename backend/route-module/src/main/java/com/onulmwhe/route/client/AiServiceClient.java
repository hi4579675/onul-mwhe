package com.onulmwhe.route.client;

import com.onulmwhe.route.dto.RouteGenerateRequest;
import com.onulmwhe.route.dto.RouteGenerateResponse;
import io.github.resilience4j.circuitbreaker.annotation.CircuitBreaker;
import io.github.resilience4j.retry.annotation.Retry;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

@Component
public class AiServiceClient {

    private final WebClient webClient;

    public AiServiceClient(
        WebClient.Builder webClientBuilder,
        @Value("${ai.service.url}") String aiServiceBaseUrl
    ) {
        this.webClient = webClientBuilder.baseUrl(aiServiceBaseUrl).build();
    }

    /**
     * AI 동선 생성 API 호출
     * @Retry: 실패 시 재시도 수행
     * @CircuitBreaker: 장애 확산 방지를 위해 호출 차단 및 Fallback 실행
     */
    @Retry(name = "aiService")
    @CircuitBreaker(name = "aiService", fallbackMethod = "fallbackGenerate")
    public RouteGenerateResponse generateRoute(RouteGenerateRequest request, String correlationId) {
        return webClient.post()
            .uri("/api/v1/route/generate")
            .header("X-Correlation-ID", correlationId) // 분산 추적 ID 전송
            .bodyValue(request) // Request Body 설정
            .retrieve() // 응답 수신 시작
            .bodyToMono(RouteGenerateResponse.class) // JSON -> 객체 변환
            .block(); // 동기 방식으로 대기 (응답 수신까지 대기)
    }

    /**
     * AI 서비스 호출 실패 시 실행되는 대체 로직 (Fallback)
     * 파라미터는 원본 메서드와 동일해야 하며, 마지막에 Throwable을 추가함
     */
    @SuppressWarnings("unused")
    private RouteGenerateResponse fallbackGenerate(
        RouteGenerateRequest request,
        String correlationId,
        Throwable t
    ) {
        // log.error("AI Service Error: {}", t.getMessage());

        // 빈 결과와 함께 fallback_used=true를 설정하여 반환
        return new RouteGenerateResponse(
            java.util.List.of(),
            true,
            0,
            correlationId
        );
    }
}
