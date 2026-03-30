package com.onulmwhe.route.repository;

import com.onulmwhe.route.entity.Route;
import java.util.List;
import java.util.UUID;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

public interface RouteRepository extends JpaRepository<Route, UUID> {
    List<Route> findByUserIdOrderByCreatedAtDesc(String userId, Pageable pageable);
}
