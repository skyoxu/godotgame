const { test, expect } = require('@playwright/test');

const baseUrl = process.env.PROJECT_HEALTH_URL || 'http://127.0.0.1:8767';
const graph = {
  revision: 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
  main_scene: 'Game.Godot/Scenes/Main.tscn',
  nodes: {
    'Game.Godot/Scenes/Main.tscn': { classification: 'confirmed-reachable', functional_summary: {}, nodes: [] },
    'Game.Godot/Scenes/Nested.tscn': { classification: 'confirmed-reachable', functional_summary: {}, nodes: [] },
    'Game.Godot/Scenes/Deep.tscn': { classification: 'unreachable-candidate', functional_summary: {}, nodes: [] },
    'Game.Godot/Scenes/Outside.tscn': { classification: 'unreachable-candidate', functional_summary: {}, nodes: [] },
  },
  edges: [
    { source: 'Game.Godot/Scenes/Main.tscn', target: 'Game.Godot/Scenes/Nested.tscn', evidence_level: 'effective', kind: 'scene-instance' },
    { source: 'Game.Godot/Scenes/Nested.tscn', target: 'Game.Godot/Scenes/Deep.tscn', evidence_level: 'possible', kind: 'scene-instance' },
  ],
  code_references: [],
  diagnostics: [],
};

test.describe('project health template scene composition', () => {
  test('refreshes composition after delayed graph response', async ({ page }) => {
    let release;
    const released = new Promise(resolve => { release = resolve; });
    await page.route('**/api/knowledge/scene-graph', async route => {
      await released;
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(graph) });
    });
    await page.goto(baseUrl + '/knowledge/scenes');
    await page.getByRole('button', { name: 'Scene composition' }).click();
    await expect(page.locator('#scene-structure')).toContainText('No resources in this category.');
    release();
    await expect(page.locator('tr[data-resource-path="Game.Godot/Scenes/Deep.tscn"]')).toBeVisible();
  });

  test('keeps route tree selected after delayed graph response', async ({ page }) => {
    let release;
    const released = new Promise(resolve => { release = resolve; });
    await page.route('**/api/knowledge/scene-graph', async route => {
      await released;
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(graph) });
    });
    await page.goto(baseUrl + '/knowledge/scenes');
    await expect(page.getByRole('button', { name: 'Scene route tree' })).toHaveAttribute('aria-pressed', 'true');
    await expect(page.locator('.scene-composition-toolbar')).toBeHidden();
    release();
    await expect(page.locator('[data-scene-path="Game.Godot/Scenes/Main.tscn"]')).toBeVisible();
    await expect(page.locator('.scene-composition-toolbar')).toBeHidden();
  });

  test('uses route closure by default and opt-in for outside scenes', async ({ page }) => {
    await page.route('**/api/knowledge/scene-graph', route =>
      route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(graph) })
    );
    await page.goto(baseUrl + '/knowledge/scenes');
    await page.getByRole('button', { name: 'Scene composition' }).click();
    await expect(page.locator('tr[data-resource-path="Game.Godot/Scenes/Deep.tscn"]')).toBeVisible();
    await expect(page.locator('tr[data-resource-path="Game.Godot/Scenes/Outside.tscn"]')).toHaveCount(0);
    await page.locator('#include-unreachable').check();
    await expect(page.locator('tr[data-resource-path="Game.Godot/Scenes/Outside.tscn"]')).toBeVisible();
  });
});
