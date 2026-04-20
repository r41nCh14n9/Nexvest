# Step 3: Spring Boot 基礎專案撰寫與單元測試

本階段建立 Spring Boot 架構，並完成人員管理 CRUD 功能的單元測試，讓專案進入可測試的微服務形態。

---

## 3.1 專案架構

建議使用 Maven 並採用以下基本結構：

```
src/
  main/
    java/com/nexvest/
      NexvestApplication.java
      controller/
        UserController.java
      service/
        UserService.java
      model/
        User.java
      repository/
        UserRepository.java
  test/
    java/com/nexvest/
      service/
        UserServiceTest.java
      controller/
        UserControllerTest.java
pom.xml
```

---

## 3.2 Spring Boot 應用核心

`NexvestApplication.java`：

```java
package com.nexvest;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class NexvestApplication {
  public static void main(String[] args) {
    SpringApplication.run(NexvestApplication.class, args);
  }
}
```

`User.java`：

```java
package com.nexvest.model;

public class User {
  private Long id;
  private String name;
  private String email;

  public User() {}

  public User(Long id, String name, String email) {
    this.id = id;
    this.name = name;
    this.email = email;
  }

  public Long getId() {
    return id;
  }

  public void setId(Long id) {
    this.id = id;
  }

  public String getName() {
    return name;
  }

  public void setName(String name) {
    this.name = name;
  }

  public String getEmail() {
    return email;
  }

  public void setEmail(String email) {
    this.email = email;
  }
}
```

`UserService.java`：

```java
package com.nexvest.service;

import com.nexvest.model.User;
import java.util.*;
import org.springframework.stereotype.Service;

@Service
public class UserService {
  private final Map<Long, User> store = new HashMap<>();
  private long nextId = 1;

  public User createUser(User user) {
    user.setId(nextId++);
    store.put(user.getId(), user);
    return user;
  }

  public Optional<User> getUser(Long id) {
    return Optional.ofNullable(store.get(id));
  }

  public List<User> getAllUsers() {
    return new ArrayList<>(store.values());
  }

  public Optional<User> updateUser(Long id, User update) {
    if (!store.containsKey(id)) {
      return Optional.empty();
    }
    update.setId(id);
    store.put(id, update);
    return Optional.of(update);
  }

  public boolean deleteUser(Long id) {
    return store.remove(id) != null;
  }
}
```

`UserController.java`：

```java
package com.nexvest.controller;

import com.nexvest.model.User;
import com.nexvest.service.UserService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/users")
public class UserController {

  private final UserService userService;

  public UserController(UserService userService) {
    this.userService = userService;
  }

  @PostMapping
  public ResponseEntity<User> createUser(@RequestBody User user) {
    return ResponseEntity.ok(userService.createUser(user));
  }

  @GetMapping("/{id}")
  public ResponseEntity<User> getUser(@PathVariable Long id) {
    return userService.getUser(id)
        .map(ResponseEntity::ok)
        .orElse(ResponseEntity.notFound().build());
  }

  @GetMapping
  public List<User> getAllUsers() {
    return userService.getAllUsers();
  }

  @PutMapping("/{id}")
  public ResponseEntity<User> updateUser(@PathVariable Long id, @RequestBody User user) {
    return userService.updateUser(id, user)
        .map(ResponseEntity::ok)
        .orElse(ResponseEntity.notFound().build());
  }

  @DeleteMapping("/{id}")
  public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
    return userService.deleteUser(id)
        ? ResponseEntity.noContent().build()
        : ResponseEntity.notFound().build();
  }
}
```

---

## 3.3 基礎單元測試

`UserServiceTest.java`：

```java
package com.nexvest.service;

import com.nexvest.model.User;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.util.List;
import static org.junit.jupiter.api.Assertions.*;

public class UserServiceTest {

  private UserService userService;

  @BeforeEach
  void setUp() {
    userService = new UserService();
  }

  @Test
  void createUserShouldAssignId() {
    User user = new User(null, "Alice", "alice@example.com");
    User created = userService.createUser(user);

    assertNotNull(created.getId());
    assertEquals("Alice", created.getName());
  }

  @Test
  void getAllUsersShouldReturnCreatedUsers() {
    userService.createUser(new User(null, "Alice", "alice@example.com"));
    userService.createUser(new User(null, "Bob", "bob@example.com"));

    List<User> users = userService.getAllUsers();
    assertEquals(2, users.size());
  }

  @Test
  void updateUserShouldReturnUpdatedUser() {
    User created = userService.createUser(new User(null, "Alice", "alice@example.com"));
    User update = new User(null, "Alice B.", "aliceb@example.com");

    User updated = userService.updateUser(created.getId(), update).orElseThrow();
    assertEquals("Alice B.", updated.getName());
    assertEquals(created.getId(), updated.getId());
  }

  @Test
  void deleteUserShouldRemoveUser() {
    User created = userService.createUser(new User(null, "Alice", "alice@example.com"));
    assertTrue(userService.deleteUser(created.getId()));
    assertFalse(userService.getUser(created.getId()).isPresent());
  }
}
```

---

## 3.4 Maven 測試指令

```bash
mvn clean test
```

若要包含測試覆蓋率，可加上 JaCoCo：

```bash
mvn clean test jacoco:report
```

---

## 3.5 Harness Pipeline 中加入單元測試

在 `.harness/build-pipeline.yaml` 添加：

```yaml
- name: unit-tests
  type: run
  spec:
    container: maven:3.9-eclipse-temurin-17
    script: mvn clean test
```

---

## 3.6 結論

完成 step3 後，你應該已經具備：

- Spring Boot 基礎專案架構
- 人員管理 CRUD 功能的基礎實作
- 可執行的單元測試
- Harness Pipeline 中運行測試的能力

