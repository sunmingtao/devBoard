# ---------- Stage 1: Build ----------
FROM maven:3.9.9-eclipse-temurin-25 AS builder

WORKDIR /build

# 先复制 pom.xml（利用缓存）
COPY pom.xml .

# 下载依赖（加速后续 build）
RUN mvn dependency:go-offline

# 再复制源码
COPY src ./src

# 构建 jar
RUN mvn clean package -DskipTests


# ---------- Stage 2: Runtime ----------
FROM eclipse-temurin:25-jre-jammy

WORKDIR /app

# 从 build 阶段复制 jar
COPY --from=builder /build/target/devboard-*.jar app.jar

# 暴露端口
EXPOSE 8080

# JVM 优化
ENV JAVA_OPTS="-XX:+UseContainerSupport -Xmx512m"

# 启动
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]
