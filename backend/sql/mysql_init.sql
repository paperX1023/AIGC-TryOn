CREATE DATABASE IF NOT EXISTS `aigc_tryon`
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE `aigc_tryon`;

CREATE TABLE IF NOT EXISTS `users` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(64) NOT NULL,
  `password_hash` VARCHAR(255) DEFAULT NULL,
  `nickname` VARCHAR(64) DEFAULT NULL,
  `email` VARCHAR(128) DEFAULT NULL,
  `phone` VARCHAR(32) DEFAULT NULL,
  `avatar_url` TEXT DEFAULT NULL,
  `gender` VARCHAR(16) DEFAULT NULL,
  `birthday` DATE DEFAULT NULL,
  `height_cm` DECIMAL(5,2) DEFAULT NULL,
  `weight_kg` DECIMAL(5,2) DEFAULT NULL,
  `preferred_styles` JSON DEFAULT NULL,
  `bio` TEXT DEFAULT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_users_username` (`username`),
  UNIQUE KEY `uq_users_email` (`email`),
  UNIQUE KEY `uq_users_phone` (`phone`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `body_analysis_records` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` INT UNSIGNED NOT NULL,
  `image_path` TEXT NOT NULL,
  `image_url` TEXT NOT NULL,
  `gender` VARCHAR(16) NOT NULL,
  `body_shape` VARCHAR(32) NOT NULL,
  `shoulder_type` VARCHAR(32) NOT NULL,
  `waist_type` VARCHAR(32) NOT NULL,
  `leg_ratio` VARCHAR(32) NOT NULL,
  `analysis_summary` TEXT NOT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_body_analysis_user_id` (`user_id`),
  CONSTRAINT `fk_body_analysis_user`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `chat_sessions` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `session_code` VARCHAR(64) NOT NULL,
  `user_id` INT UNSIGNED DEFAULT NULL,
  `title` VARCHAR(120) DEFAULT NULL,
  `latest_body_analysis_id` INT UNSIGNED DEFAULT NULL,
  `status` VARCHAR(20) NOT NULL DEFAULT 'active',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_chat_sessions_session_code` (`session_code`),
  KEY `idx_chat_sessions_user_id` (`user_id`),
  KEY `idx_chat_sessions_latest_body_analysis_id` (`latest_body_analysis_id`),
  CONSTRAINT `fk_chat_sessions_user`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
    ON DELETE SET NULL,
  CONSTRAINT `fk_chat_sessions_body_analysis`
    FOREIGN KEY (`latest_body_analysis_id`) REFERENCES `body_analysis_records` (`id`)
    ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `chat_messages` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `chat_session_id` INT UNSIGNED NOT NULL,
  `role` VARCHAR(20) NOT NULL,
  `content` TEXT NOT NULL,
  `parsed_result` JSON DEFAULT NULL,
  `recommend_result` JSON DEFAULT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_chat_messages_session_id` (`chat_session_id`),
  CONSTRAINT `fk_chat_messages_session`
    FOREIGN KEY (`chat_session_id`) REFERENCES `chat_sessions` (`id`)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `recommendation_records` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` INT UNSIGNED NOT NULL,
  `chat_session_id` INT UNSIGNED DEFAULT NULL,
  `source` VARCHAR(20) NOT NULL,
  `input_summary` JSON NOT NULL,
  `recommend_result` JSON NOT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_recommendation_user_id` (`user_id`),
  KEY `idx_recommendation_session_id` (`chat_session_id`),
  CONSTRAINT `fk_recommendation_user`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
    ON DELETE CASCADE,
  CONSTRAINT `fk_recommendation_session`
    FOREIGN KEY (`chat_session_id`) REFERENCES `chat_sessions` (`id`)
    ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `tryon_records` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` INT UNSIGNED DEFAULT NULL,
  `chat_session_id` INT UNSIGNED DEFAULT NULL,
  `body_analysis_record_id` INT UNSIGNED DEFAULT NULL,
  `person_image_path` TEXT NOT NULL,
  `person_image_url` TEXT NOT NULL,
  `cloth_image_path` TEXT NOT NULL,
  `cloth_image_url` TEXT NOT NULL,
  `result_image_path` TEXT NOT NULL,
  `result_image_url` TEXT NOT NULL,
  `status` VARCHAR(20) NOT NULL,
  `message` TEXT NOT NULL,
  `source` VARCHAR(20) NOT NULL DEFAULT 'mock',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_tryon_user_id` (`user_id`),
  KEY `idx_tryon_session_id` (`chat_session_id`),
  KEY `idx_tryon_body_analysis_id` (`body_analysis_record_id`),
  CONSTRAINT `fk_tryon_user`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
    ON DELETE SET NULL,
  CONSTRAINT `fk_tryon_session`
    FOREIGN KEY (`chat_session_id`) REFERENCES `chat_sessions` (`id`)
    ON DELETE SET NULL,
  CONSTRAINT `fk_tryon_body_analysis`
    FOREIGN KEY (`body_analysis_record_id`) REFERENCES `body_analysis_records` (`id`)
    ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `wardrobe_items` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` INT UNSIGNED NOT NULL,
  `name` VARCHAR(120) NOT NULL,
  `category` VARCHAR(32) NOT NULL DEFAULT '上衣',
  `image_path` TEXT NOT NULL,
  `image_url` TEXT NOT NULL,
  `detection_result` JSON DEFAULT NULL,
  `source` VARCHAR(20) NOT NULL DEFAULT 'user',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_wardrobe_user_id` (`user_id`),
  CONSTRAINT `fk_wardrobe_user`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
