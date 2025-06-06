# Docker MySQL Setup Guide

## Installing Docker on macOS

### Option 1: Docker Desktop (Recommended)
1. Download Docker Desktop from: https://www.docker.com/products/docker-desktop/
2. Install the `.dmg` file
3. Launch Docker Desktop from Applications
4. Wait for Docker to start (whale icon in menu bar)

### Option 2: Using Homebrew
```bash
# Install Docker Desktop via Homebrew
brew install --cask docker

# Launch Docker Desktop
open /Applications/Docker.app
```

### Verify Installation
```bash
docker --version
docker-compose --version
```

## Starting MySQL with Docker

### Using docker-compose (Recommended)
We've created a `docker-compose.yml` file with the following configuration:
- MySQL 8.0
- Database name: `devboard`
- Username: `devboard_user`
- Password: `devboard_pass`
- Port: 3306

### Start MySQL
```bash
# Start MySQL container
docker-compose up -d

# Check if container is running
docker ps

# View logs
docker-compose logs mysql
```

### Stop MySQL
```bash
# Stop the container
docker-compose down

# Stop and remove volumes (deletes all data)
docker-compose down -v
```

## Alternative: Using Docker Run Command
If you prefer not to use docker-compose:

```bash
# Run MySQL container
docker run -d \
  --name devboard-mysql \
  -e MYSQL_ROOT_PASSWORD=rootpassword \
  -e MYSQL_DATABASE=devboard \
  -e MYSQL_USER=devboard_user \
  -e MYSQL_PASSWORD=devboard_pass \
  -p 3306:3306 \
  mysql:8.0

# Stop container
docker stop devboard-mysql

# Remove container
docker rm devboard-mysql
```

## Connecting to MySQL

### Using MySQL Client
```bash
# Connect as root
mysql -h localhost -P 3306 -u root -prootpassword

# Connect as devboard_user
mysql -h localhost -P 3306 -u devboard_user -pdevboard_pass devboard
```

### Using Docker Exec
```bash
# Access MySQL inside container
docker exec -it devboard-mysql mysql -u root -prootpassword

# Or access bash first
docker exec -it devboard-mysql bash
mysql -u root -prootpassword
```

## Spring Boot Configuration

Update your `application.yml` to use MySQL:

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/devboard
    driver-class-name: com.mysql.cj.jdbc.Driver
    username: devboard_user
    password: devboard_pass
  
  jpa:
    database-platform: org.hibernate.dialect.MySQL8Dialect
    hibernate:
      ddl-auto: update  # Use 'create-drop' for development
    show-sql: true
```

## Useful Docker Commands

```bash
# List all containers
docker ps -a

# View container logs
docker logs devboard-mysql

# Stop all containers
docker stop $(docker ps -aq)

# Remove all containers
docker rm $(docker ps -aq)

# List volumes
docker volume ls

# Remove unused volumes
docker volume prune
```

## Troubleshooting

### Port Already in Use
If port 3306 is already in use:
```bash
# Find process using port 3306
lsof -i :3306

# Change port in docker-compose.yml
ports:
  - "3307:3306"  # Use 3307 on host
```

### Connection Refused
- Make sure Docker Desktop is running
- Check if container is running: `docker ps`
- Check logs: `docker logs devboard-mysql`

### Permission Denied
- Make sure Docker Desktop has necessary permissions
- On macOS, you might need to grant full disk access to Docker

## Benefits of Using Docker for MySQL

1. **No Installation**: No need to install MySQL on your machine
2. **Version Control**: Easy to switch MySQL versions
3. **Isolation**: Doesn't conflict with other MySQL installations
4. **Reproducible**: Same setup on any machine
5. **Easy Cleanup**: Just remove container and volume

## Next Steps

1. Install Docker Desktop
2. Run `docker-compose up -d` in project root
3. Update Spring Boot configuration
4. Test connection with your application