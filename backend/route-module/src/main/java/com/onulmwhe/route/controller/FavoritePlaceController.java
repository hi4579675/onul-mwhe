package com.onulmwhe.route.controller;

import com.onulmwhe.route.dto.FavoritePlaceRequest;
import com.onulmwhe.route.dto.FavoritePlaceResponse;
import com.onulmwhe.route.service.FavoritePlaceService;
import java.util.List;
import lombok.AllArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/places/favorites")
@AllArgsConstructor
public class FavoritePlaceController {

    private static final String USER_ID_HEADER = "X-User-Id";

    private final FavoritePlaceService favoritePlaceService;

    @PostMapping
    public ResponseEntity<FavoritePlaceResponse> create(
        @RequestHeader(value = USER_ID_HEADER) String userId,
        @RequestBody FavoritePlaceRequest request
    ) {
        return ResponseEntity.ok(favoritePlaceService.create(userId, request));
    }

    @GetMapping
    public ResponseEntity<List<FavoritePlaceResponse>> list(
        @RequestHeader(value = USER_ID_HEADER) String userId
    ) {
        return ResponseEntity.ok(favoritePlaceService.list(userId));
    }

    @DeleteMapping("/{placeId}")
    public ResponseEntity<Void> delete(
        @RequestHeader(value = USER_ID_HEADER) String userId,
        @PathVariable String placeId
    ) {
        favoritePlaceService.delete(userId, placeId);
        return ResponseEntity.noContent().build();
    }
}
