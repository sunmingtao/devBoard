# Security Configuration Guide

## JWT Secret Management

### Development Environment
For development, the application uses a default JWT secret. This is ONLY acceptable for local development.

### Production Environment
For production deployment, you MUST:

1. **Generate a strong secret key** (at least 256 bits):
   ```bash
   openssl rand -base64 32
   ```

2. **Set the environment variable**:
   ```bash
   export JWT_SECRET=your-generated-secret-key
   export JWT_EXPIRATION_MS=86400000  # 24 hours in milliseconds
   ```

3. **Never commit secrets to version control**
   - Use environment variables
   - Use secrets management services (AWS Secrets Manager, HashiCorp Vault, etc.)
   - Use Kubernetes secrets if deploying to K8s

### Running the Application with Environment Variables

#### Linux/Mac:
```bash
JWT_SECRET=your-secret-key java -jar devboard-0.0.1-SNAPSHOT.jar
```

#### Windows:
```cmd
set JWT_SECRET=your-secret-key
java -jar devboard-0.0.1-SNAPSHOT.jar
```

#### Using .env file (for local development only):
1. Copy `.env.example` to `.env`
2. Update the values
3. Use a tool like `direnv` or load manually:
   ```bash
   export $(cat .env | xargs)
   ```

### Best Practices
1. **Rotate secrets regularly** - Change JWT secrets periodically
2. **Use different secrets per environment** - Dev, staging, and production should have different secrets
3. **Monitor for exposed secrets** - Use tools like GitHub secret scanning
4. **Implement token refresh** - Don't rely solely on long-lived tokens