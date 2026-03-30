package com.onulmwhe.route.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.onulmwhe.route.client.AiServiceClient;
import com.onulmwhe.route.dto.RouteGenerateRequest;
import com.onulmwhe.route.dto.RouteGenerateResponse;
import com.onulmwhe.route.dto.RouteHistoryItemResponse;
import com.onulmwhe.route.entity.Route;
import com.onulmwhe.route.repository.RouteRepository;
import java.util.List;
import lombok.AllArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;

@Service
@AllArgsConstructor
public class RouteGenerationService {

    private static final Logger log = LoggerFactory.getLogger(RouteGenerationService.class);

    private final AiServiceClient aiServiceClient;
    private final RouteRepository routeRepository;
    private final ObjectMapper objectMapper;

    public RouteGenerateResponse generate(
        RouteGenerateRequest request,
        String userId,
        String correlationId
    ) {
        RouteGenerateResponse response = aiServiceClient.generateRoute(request, correlationId);

        try {
            String responseJson = objectMapper.writeValueAsString(response);

            Route route = Route.of(
                userId,
                request.region(),
                responseJson,
                response.fallbackUsed(),
                correlationId
            );
            routeRepository.save(route);

            log.info(
                "event=route.saved user_id={} correlation_id={} fallback={}",
                userId,
                correlationId,
                response.fallbackUsed()
            );
        } catch (Exception e) {
            log.error(
                "event=route.save.failed user_id={} correlation_id={} reason={}",
                userId,
                correlationId,
                e.getMessage(),
                e
            );
        }

        return response;
    }

    public List<RouteHistoryItemResponse> history(
        String userId,
        int limit,
        String correlationId
    ) {
        int safeLimit = Math.max(1, Math.min(limit, 50));

        List<Route> rows = routeRepository.findByUserIdOrderByCreatedAtDesc(
            userId,
            PageRequest.of(0, safeLimit)
        );

        return rows.stream()
            .map(row -> {
                try {
                    RouteGenerateResponse parsed =
                        objectMapper.readValue(row.getPlanJson(), RouteGenerateResponse.class);

                    return new RouteHistoryItemResponse(
                        row.getId(),
                        row.getUserId(),
                        row.getRegion(),
                        parsed,
                        row.getCreatedAt()
                    );
                } catch (Exception e) {
                    log.error(
                        "[{}] route.history.parse.failed id={} reason={}",
                        correlationId,
                        row.getId(),
                        e.getMessage()
                    );
                    return null;
                }
            })
            .filter(java.util.Objects::nonNull)
            .toList();
    }
}
