package com.brochure;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.domain.EntityScan;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;

@SpringBootApplication
@ComponentScan(basePackages = {"com.brochure"})
@EntityScan("com.brochure.model")
@EnableJpaRepositories("com.brochure.repository")
public class BrochureApplication {
    public static void main(String[] args) {
        SpringApplication.run(BrochureApplication.class, args);
    }
}
