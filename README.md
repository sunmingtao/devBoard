# DevBoard - Developer Task Board System

![Backend CI/CD](https://github.com/sunmingtao/devBoard/workflows/Backend%20CI%2FCD/badge.svg)

A modern task management system built with Spring Boot and Vue.js for demonstrating full-stack development skills.

## 🚀 Quick Start

### Backend Setup (Spring Boot)

#### Using Spring Initializr Command Line

```bash
# Initialize Spring Boot project with required dependencies
curl https://start.spring.io/starter.zip \
  -d dependencies=web,data-jpa,lombok,mysql \
  -d type=maven-project \
  -d language=java \
  -d bootVersion=3.3.0 \
  -d baseDir=devboard-backend \
  -d groupId=com.example \
  -d artifactId=devboard \
  -d name=devboard \
  -d description="Developer Task Board System" \
  -d packageName=com.example.devboard \
  -d packaging=jar \
  -d javaVersion=21 \
  -o devboard-backend.zip

# Extract the project
unzip devboard-backend.zip
rm devboard-backend.zip
```

#### Alternative: Using Spring Initializr Web UI

1. Visit [https://start.spring.io/](https://start.spring.io/)
2. Configure the project:
   - **Project:** Maven
   - **Language:** Java
   - **Spring Boot:** 3.3.0
   - **Group:** com.example
   - **Artifact:** devboard
   - **Name:** devboard
   - **Description:** Developer Task Board System
   - **Package name:** com.example.devboard
   - **Packaging:** Jar
   - **Java:** 21

3. Add Dependencies:
   - Spring Web
   - Spring Data JPA
   - Lombok
   - MySQL Driver

4. Click **Generate** to download the project

### Running the Application

```bash
cd devboard-backend

# Run with Maven wrapper (no Maven installation required)
./mvnw spring-boot:run

# Or if you have Maven installed
mvn spring-boot:run
```

The application will start on `http://localhost:8080`

## 📦 Project Structure

```
devboard-backend/
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/example/devboard/
│   │   │       └── DevboardApplication.java
│   │   └── resources/
│   │       ├── application.properties
│   │       ├── static/
│   │       └── templates/
│   └── test/
├── pom.xml
├── mvnw
├── mvnw.cmd
└── .gitignore
```

## 🛠️ Technologies

- **Backend:** Spring Boot 3.3.0, Java 21
- **Database:** MySQL (via Spring Data JPA)
- **Build Tool:** Maven
- **Utilities:** Lombok

## 📝 Next Steps

1. Configure MySQL database connection in `application.properties`
2. Create entity models for the task board
3. Implement REST API endpoints
4. Set up JWT authentication
5. Add frontend with Vue.js 3

## 🎯 Features (To Be Implemented)

- User authentication (JWT)
- Task management (Create, Read, Update, Delete)
- Kanban board view (To Do, In Progress, Done)
- User roles and permissions
- Admin dashboard