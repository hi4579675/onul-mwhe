package com.onulmwhe.route.controller;

import com.onulmwhe.route.dto.RouteGenerateRequest;
import com.onulmwhe.route.dto.RouteGenerateResponse;
import com.onulmwhe.route.service.RouteGenerationService;
import java.util.UUID;
import org.springframework.http.HttpHeaders;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/routes")
public class RouteController {

    private static final String CORRELATION_HEADER = "X-Correlation-ID";

    private final RouteGenerationService routeGenerationService;

    public RouteController(RouteGenerationService routeGenerationService) {
        this.routeGenerationService = routeGenerationService;
    }

    @PostMapping("/generate")
    public ResponseEntity<RouteGenerateResponse> generate(
        @RequestBody RouteGenerateRequest request,
        @RequestHeader(value = CORRELATION_HEADER, required = false) String correlationId
    ) {
        String resolvedCorrelationId = (correlationId == null || correlationId.isBlank())
            ? UUID.randomUUID().toString()
            : correlationId;

        RouteGenerateResponse response = routeGenerationService.generate(request, resolvedCorrelationId);

        return ResponseEntity.ok()
            .header(CORRELATION_HEADER, resolvedCorrelationId)
            .body(response);
    }
}
