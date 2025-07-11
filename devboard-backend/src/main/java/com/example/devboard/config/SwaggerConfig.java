package com.example.devboard.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.License;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class SwaggerConfig {
    
    @Bean
    public OpenAPI devBoardOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("DevBoard API")
                        .description("Developer Task Board System REST API Documentation")
                        .version("1.0.0")
                        .contact(new Contact()
                                .name("DevBoard Team")
                                .email("devboard@example.com"))
                        .license(new License()
                                .name("Apache 2.0")
                                .url("http://www.apache.org/licenses/LICENSE-2.0")));
    }
}