# ---------- Stage 1: Build ----------
FROM eclipse-temurin:25-jdk-jammy AS builder

WORKDIR /build

COPY .mvn ./.mvn
COPY mvnw pom.xml ./
RUN ./mvnw dependency:go-offline

COPY src ./src
RUN ./mvnw clean package -DskipTests


# ---------- Stage 2: Runtime ----------
FROM eclipse-temurin:25-jre-jammy

WORKDIR /app

COPY --from=builder /build/target/event-service-*.jar app.jar

ENV JAVA_OPTS="-XX:+UseContainerSupport -Xmx256m"

ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]
