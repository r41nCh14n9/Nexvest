
# Step 4: 整合測試與完整流程驗證

本階段將驗證整合測試流程，並觀察從代碼提交到部署的完整路徑是否正確。

---

## 4.1 整合測試概念

整合測試檢查系統組件在一起運作是否正常，例如：

- API 與資料庫是否連線
- 服務啟動後是否回應健康檢查
- 不同模組之間的邊界是否正確

---

## 4.2 整合測試範例

```java
package com.nexvest.integration;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest.WebEnvironment;
import static org.assertj.core.api.Assertions.*;

@SpringBootTest(webEnvironment = WebEnvironment.RANDOM_PORT)
public class AppIntegrationTest {

  @Autowired
  private TestRestTemplate restTemplate;

  @Test
  void healthEndpointShouldReturnOk() {
    String body = this.restTemplate.getForObject("/actuator/health", String.class);
    assertThat(body).contains("UP");
  }

  @Test
  void createUserEndpointShouldCreateUser() {
    User user = new User(null, "Alice", "alice@example.com");
    ResponseEntity<User> response = this.restTemplate.postForEntity("/api/users", user, User.class);

    assertEquals(201, response.getStatusCodeValue());
    assertNotNull(response.getBody().getId());
  }

  @Test
  void getUserEndpointShouldReturnUser() {
    User created = new User(null, "Bob", "bob@example.com");
    ResponseEntity<User> createResponse = this.restTemplate.postForEntity("/api/users", created, User.class);
    Long id = createResponse.getBody().getId();

    ResponseEntity<User> getResponse = this.restTemplate.getForEntity("/api/users/" + id, User.class);

    assertEquals(200, getResponse.getStatusCodeValue());
    assertEquals(created.getName(), getResponse.getBody().getName());
  }

  @Test
  void getAllUsersEndpointShouldReturnAllUsers() {
    User user1 = new User(null, "Charlie", "charlie@example.com");
    ResponseEntity<User> createResponse1 = this.restTemplate.postForEntity("/api/users", user1, User.class);
    User user2 = new User(null, "David", "david@example.com");
    ResponseEntity<User> createResponse2 = this.restTemplate.postForEntity("/api/users", user2, User.class);

    ResponseEntity<List<User>> getAllResponse = this.restTemplate.getForEntity("/api/users", List.class);

    assertEquals(200, getAllResponse.getStatusCodeValue());
    assertEquals(2, getAllResponse.getBody().size());
  }

  @Test
  void updateUserEndpointShouldUpdateUser() {
    User created = new User(null, "Eve", "eve@example.com");
    ResponseEntity<User> createResponse = this.restTemplate.postForEntity("/api/users", created, User.class);
    Long id = createResponse.getBody().getId();
    User update = new User(id, "Eve Update", "eveupdate@example.com");

    ResponseEntity<User> updateResponse = this.restTemplate.putForEntity("/api/users/" + id, update, User.class);

    assertEquals(200, updateResponse.getStatusCodeValue());
    assertEquals("Eve Update", updateResponse.getBody().getName());
  }

  @Test
  void deleteUserEndpointShouldDeleteUser() {
    User created = new User(null, "Frank", "frank@example.com");
    ResponseEntity<User> createResponse = this.restTemplate.postForEntity("/api/users", created, User.class);
    Long id = createResponse.getBody().getId();

    ResponseEntity<Void> deleteResponse = this.restTemplate.deleteWithEntity("/api/users/" + id, Void.class);

    assertEquals(204, deleteResponse.getStatusCodeValue());
  }
}
```

---

## 4.3 Pipeline 完整流程

在 `.harness/build-pipeline.yaml` 建立完整 Flow：

```yaml
version: 1
kind: pipeline
metadata:
  name: nexvest-full-flow
  identifier: nexvest_full_flow
spec:
  stages:
    - name: build
      type: ci
      spec:
        steps:
          - name: compile
            type: run
            spec:
              container: maven:3.9-eclipse-temurin-17
              script: mvn clean package -DskipTests

    - name: unit-test
      type: ci
      depends_on:
        - build
      spec:
        steps:
          - name: run-unit-tests
            type: run
            spec:
              container: maven:3.9-eclipse-temurin-17
              script: mvn test

    - name: integration-test
      type: ci
      depends_on:
        - unit-test
      spec:
        steps:
          - name: run-integration-tests
            type: run
            spec:
              container: maven:3.9-eclipse-temurin-17
              script: mvn verify

    - name: deploy-dev
      type: deployment
      depends_on:
        - integration-test
      spec:
        environment: nexvest-dev
        deployment_type: kubernetes
        steps:
          - name: deploy-to-k8s
            type: apply
            spec:
              manifests:
                - k8s/dev/deployment.yaml
                - k8s/dev/service.yaml
              namespace: nexvest-dev
```

---

## 4.4 完整流程驗證

1. 在 Harness 觸發 Pipeline
2. 確認 build、unit-test、integration-test、deploy-dev 都成功
3. 驗證 `http://localhost:8080/actuator/health`
4. 驗證 `/api/users` 的 CRUD 功能是否正常工作

---

## 4.5 結論

完成 step4 後，你應該已經驗證：

- 專案從開發到部署流程正常
- 單元測試與整合測試都納入 Pipeline
- 部署目標環境可用