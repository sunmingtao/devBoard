# JWT Secret Length Error - Issue Documentation

## Issue Title
JWT Secret Key Too Short - WeakKeyException (200 bits required)

## Issue Description
When attempting to start the Spring Boot application with JWT authentication enabled, the application fails to initialize with the following error:

```
java.security.InvalidKeyException: The specified key byte array is 192 bits which is not secure enough for any JWT HMAC-SHA algorithm. The JWT JWA Specification (RFC 7518, Section 3.2) states that keys used with HMAC-SHA algorithms MUST have a size >= 256 bits (the key size must be greater than or equal to the hash output size). Consider using the Jwts.SIG.HS256.key() builder (or HS384.key() or HS512.key()) to create a key guaranteed to be secure enough for your preferred HMAC-SHA algorithm. See https://tools.ietf.org/html/rfc7518#section-3.2 for more information.
```

## Root Cause
The JWT secret key configured in the application properties is too short. The current secret "mySecretKey" is only 88 bits (11 characters), while JWT specifications require at least 256 bits for HMAC-SHA256 algorithm.

## Affected Files
- `devboard-backend/src/main/resources/application.yml`
- `devboard-backend/src/main/resources/application-dev.yml`
- `devboard-backend/src/main/resources/application-mysql.yml`

## Resolution Steps

### 1. Generate a Secure Secret Key
Generate a base64-encoded secret key with at least 256 bits (32 bytes):

**Option A - Using OpenSSL:**
```bash
openssl rand -base64 32
```

**Option B - Using Java:**
```java
import io.jsonwebtoken.SignatureAlgorithm;
import io.jsonwebtoken.security.Keys;
import java.util.Base64;

byte[] keyBytes = Keys.secretKeyFor(SignatureAlgorithm.HS256).getEncoded();
String base64Secret = Base64.getEncoder().encodeToString(keyBytes);
System.out.println(base64Secret);
```

### 2. Update Configuration Files
Replace the JWT secret in all application property files with the generated secure key:

**application.yml:**
```yaml
jwt:
  secret: "YOUR_GENERATED_BASE64_SECRET_HERE"  # Must be at least 32 bytes when decoded
  expiration: 86400000
```

**application-dev.yml:**
```yaml
jwt:
  secret: "YOUR_GENERATED_BASE64_SECRET_HERE"
  expiration: 86400000
```

**application-mysql.yml:**
```yaml
jwt:
  secret: "YOUR_GENERATED_BASE64_SECRET_HERE"
  expiration: 86400000
```

### 3. Security Best Practices
1. **Never commit real secrets to version control** - Use environment variables or external configuration
2. **Use different secrets for different environments** (dev, staging, production)
3. **Rotate secrets regularly**
4. **Store secrets securely** using tools like:
   - Environment variables
   - AWS Secrets Manager
   - HashiCorp Vault
   - Kubernetes Secrets

### 4. Environment Variable Configuration (Recommended)
Instead of hardcoding the secret, use environment variables:

**application.yml:**
```yaml
jwt:
  secret: ${JWT_SECRET:defaultSecretForLocalDevelopmentOnly}
  expiration: 86400000
```

Then set the environment variable:
```bash
export JWT_SECRET="your-secure-base64-encoded-secret"
```

## Prevention
- Add validation in application startup to check JWT secret length
- Include JWT secret generation in project setup documentation
- Use Spring Boot configuration validation annotations

## Related Links
- [JWT RFC 7518 Section 3.2](https://tools.ietf.org/html/rfc7518#section-3.2)
- [Spring Security JWT Documentation](https://docs.spring.io/spring-security/reference/servlet/oauth2/resource-server/jwt.html)