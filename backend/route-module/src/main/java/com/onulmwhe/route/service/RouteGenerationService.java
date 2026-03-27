package com.onulmwhe.route.service;

import com.onulmwhe.route.client.AiServiceClient;
import com.onulmwhe.route.dto.RouteGenerateRequest;
import com.onulmwhe.route.dto.RouteGenerateResponse;
import org.springframework.stereotype.Service;

@Service
public class RouteGenerationService {
    private final AiServiceClient aiServiceClient;
    public RouteGenerationService(AiServiceClient aiServiceClient) {
        this.aiServiceClient = aiServiceClient;
    }
    public RouteGenerateResponse generate(RouteGenerateRequest request, String correlationId) {
        return aiServiceClient.generateRoute(request, correlationId);
    }
}
