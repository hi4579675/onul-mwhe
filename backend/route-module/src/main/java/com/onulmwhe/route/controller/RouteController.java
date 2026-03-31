package com.onulmwhe.route.controller;

import com.onulmwhe.route.dto.RouteGenerateRequest;
import com.onulmwhe.route.dto.RouteGenerateResponse;
import com.onulmwhe.route.dto.RouteHistoryItemResponse;
import com.onulmwhe.route.service.RouteGenerationService;
import java.util.List;
import java.util.UUID;
import lombok.AllArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/routes")
@AllArgsConstructor
public class RouteController {

    private static final String CORRELATION_HEADER = "X-Correlation-ID";


    private final RouteGenerationService routeGenerationService;

    @PostMapping("/generate")
    public ResponseEntity<RouteGenerateResponse> generate(
        @RequestBody RouteGenerateRequest request,
        @RequestHeader(value = CORRELATION_HEADER, required = false) String correlationId,
        // JwtAuthenticationFilter가 SecurityContext에 설정한 principal(userId)을 주입.
        // principal 타입이 String이므로 @AuthenticationPrincipal String으로 직접 바인딩 가능.
        @AuthenticationPrincipal String userId
    ) {
        String cid = resolveCorrelationId(correlationId);
        RouteGenerateResponse response = routeGenerationService.generate(request, userId, cid);
        return ResponseEntity.ok()
            .header(CORRELATION_HEADER, cid)
            .body(response);
    }

    @GetMapping("/history")
    public ResponseEntity<List<RouteHistoryItemResponse>> history(
        @AuthenticationPrincipal String userId,
        @RequestParam(defaultValue = "20") int limit,
        @RequestHeader(value = CORRELATION_HEADER, required = false) String correlationId
    ) {
        String cid = resolveCorrelationId(correlationId);
        List<RouteHistoryItemResponse> response = routeGenerationService.history(userId, limit, cid);
        return ResponseEntity.ok()
            .header(CORRELATION_HEADER, cid)
            .body(response);
    }

    private String resolveCorrelationId(String correlationId) {
        return (correlationId == null || correlationId.isBlank())
            ? UUID.randomUUID().toString()
            : correlationId;
    }
}
