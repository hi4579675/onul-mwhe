package com.onulmwhe.route.controller;

import com.onulmwhe.route.dto.FavoritePlaceRequest;
import com.onulmwhe.route.dto.FavoritePlaceResponse;
import com.onulmwhe.route.service.FavoritePlaceService;
import java.util.List;
import lombok.AllArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/places/favorites")
@AllArgsConstructor
public class FavoritePlaceController {

    // X-User-Id 헤더 제거: JWT SecurityContext에서 userId 추출.

    private final FavoritePlaceService favoritePlaceService;

    @PostMapping
    public ResponseEntity<FavoritePlaceResponse> create(
        @AuthenticationPrincipal String userId,
        @RequestBody FavoritePlaceRequest request
    ) {
        return ResponseEntity.ok(favoritePlaceService.create(userId, request));
    }

    @GetMapping
    public ResponseEntity<List<FavoritePlaceResponse>> list(
        @AuthenticationPrincipal String userId
    ) {
        return ResponseEntity.ok(favoritePlaceService.list(userId));
    }

    @DeleteMapping("/{placeId}")
    public ResponseEntity<Void> delete(
        @AuthenticationPrincipal String userId,
        @PathVariable String placeId
    ) {
        favoritePlaceService.delete(userId, placeId);
        return ResponseEntity.noContent().build();
    }
}
