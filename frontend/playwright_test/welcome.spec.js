import { test, expect } from '@playwright/test';

test.describe('RAG Documentation Assistant - Welcome Screen (Scenario 1)', () => {
  
  test.beforeEach(async ({ page }) => {
    // Go to the main page
    await page.goto('/');
  });

  test('should display initial welcome screen elements correctly', async ({ page }) => {
    // Verify the title in header
    const brandTitle = page.locator('.header-title-btn');
    await expect(brandTitle).toBeVisible();
    await expect(brandTitle).toHaveText('Documentation Assistant');

    // Verify the welcome container titles
    const welcomeTitle = page.locator('.welcome-title').first();
    await expect(welcomeTitle).toBeVisible();
    await expect(welcomeTitle).toHaveText('RAG Documentation Assistant');

    // Verify sample questions list and suggestions
    const suggestionsHeader = page.locator('.welcome-title').nth(1);
    await expect(suggestionsHeader).toHaveText('Sample Questions:');

    // Check all 4 suggestions exist and are visible
    const chip0 = page.locator('#suggestion-0');
    const chip1 = page.locator('#suggestion-1');
    const chip2 = page.locator('#suggestion-2');
    const chip3 = page.locator('#suggestion-3');

    await expect(chip0).toBeVisible();
    await expect(chip0).toHaveText('How do I create background tasks in FastAPI?');

    await expect(chip1).toBeVisible();
    await expect(chip1).toHaveText('Explain FastAPI dependency injection');

    await expect(chip2).toBeVisible();
    await expect(chip2).toHaveText('How to handle file uploads in FastAPI?');

    await expect(chip3).toBeVisible();
    await expect(chip3).toHaveText('What are path parameters vs query parameters?');

    // Verify sources panel empty state
    const emptySourcesText = page.locator('.sources-empty-text');
    await expect(emptySourcesText).toBeVisible();
    await expect(emptySourcesText).toHaveText('Sources will appear here after you ask a question.');

    // Verify the chat input bar
    const chatInput = page.locator('#chat-input');
    await expect(chatInput).toBeVisible();
    await expect(chatInput).toBeEmpty();
    await expect(chatInput).toBeEnabled();

    const sendButton = page.locator('#send-button');
    await expect(sendButton).toBeVisible();
    await expect(sendButton).toBeEnabled();
    await expect(sendButton).toHaveText('Submit');
  });

});
