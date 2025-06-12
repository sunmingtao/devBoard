# Use OpenJDK 21 as the base image
# This provides Java 21 runtime environment
FROM openjdk:21-jdk-slim

# Set working directory inside container
# All subsequent commands will run from this directory
WORKDIR /app

# Copy the built JAR file from target/ to container
# We'll build this JAR first using Maven
COPY target/devboard-*.jar app.jar

# Expose port 8080 
# This tells Docker that our app uses port 8080
# (Doesn't actually publish the port - that's done with -p flag when running)
EXPOSE 8080

# Set JVM options for better container performance
# -XX:+UseContainerSupport: Make JVM aware it's running in container
# -Xmx512m: Limit memory usage to 512MB
ENV JAVA_OPTS="-XX:+UseContainerSupport -Xmx512m"

# Command to run when container starts
# This starts our Spring Boot application
CMD ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]