CREATE TABLE brochure_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT NOT NULL,
    hotel_name VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    exterior_image VARCHAR(255),
    room_image VARCHAR(255),
    restaurant_image VARCHAR(255),
    prompt TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
