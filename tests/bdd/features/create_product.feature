Feature: Create product

  Background:
    Given a sample product

  Scenario: Create product successfully
    Given the repository will return the product with id "new-id"
    When I execute create_product
    Then the result id should be "new-id"
    And the result price should be 12.5
    And the repository create must be awaited once

  Scenario: Negative price raises
    Given a sample product with price -1
    When I execute create_product
    Then a ValueError should be raised with message "Price cannot be negative"
    And the repository create must not be called
