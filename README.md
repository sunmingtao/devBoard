# DevBoard - Developer Task Board System

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
- **Frontend:** Vue.js 3, TypeScript
- **Database:** MySQL (via Spring Data JPA)
- **Build Tool:** Maven
- **Infrastructure:** Terraform
- **CI/CD:** GitHub Actions
- **Cloud Services:** AWS (ECS, RDS, S3, CloudFront)
- **Utilities:** Lombok

