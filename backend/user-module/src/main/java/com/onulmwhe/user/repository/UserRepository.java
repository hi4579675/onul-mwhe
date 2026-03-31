package com.onulmwhe.user.repository;

import com.onulmwhe.user.entity.User;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface UserRepository extends JpaRepository<User, Long> {

    /**
     * OAuth2 로그인 시 upsert 판단에 사용.
     * provider + providerId 조합이 유니크 키.
     */
    Optional<User> findByProviderAndProviderId(String provider, String providerId);

    /**
     * JWT 검증 후 userId로 사용자 조회할 때 사용.
     * (현재 플로우에서는 JWT subject만으로 충분하지만,
     *  향후 프로필 API 등에서 필요할 수 있어 미리 선언)
     */
    Optional<User> findByUserId(String userId);
}
