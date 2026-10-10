import { expect, test } from '@playwright/test'
import path from 'node:path'
import AxeBuilder from '@axe-core/playwright'

test('home and mobile navigation render without layout overflow', async ({ page }, info) => {
  await page.goto('/')
  await expect(
    page.getByRole('heading', { name: 'Lost something on campus? FindIt can help.' }),
  ).toBeVisible()
  await expect(page.getByRole('article').first()).toBeVisible()
  await expect(
    page.getByRole('navigation', { name: 'Main navigation' }).getByRole('link'),
  ).toHaveCount(3)
  await page.evaluate(() => document.fonts.ready)
  await page.screenshot({ path: info.outputPath('home-desktop.png'), fullPage: true })
  await page.setViewportSize({ width: 390, height: 844 })
  await expect(page.getByRole('button', { name: 'Open menu' })).toBeVisible()
  await page.screenshot({ path: info.outputPath('home-mobile.png'), fullPage: true })
  expect(
    await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth),
  ).toBeTruthy()
  await page.getByRole('button', { name: 'Open menu' }).click()
  await page
    .getByRole('navigation', { name: 'Mobile navigation' })
    .getByRole('link', { name: 'Report' })
    .click()
  await expect(page.getByRole('heading', { name: 'What happened?' })).toBeVisible()
  await page.getByRole('link', { name: /I lost something/ }).click()
  await expect(page.getByRole('heading', { name: 'Tell us what’s missing.' })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Open menu' })).toBeVisible()
  await page.screenshot({ path: info.outputPath('form-mobile.png'), fullPage: true })
  expect(
    await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth),
  ).toBeTruthy()
})

test('real lost/found forms, photos, AI matches, filters and deletion', async ({
  page,
  request,
}, info) => {
  const created: number[] = []
  const name = `Test blue backpack ${Date.now()}`
  const image = path.resolve('../data/synthetic/images/4.png')
  try {
    for (const kind of ['lost', 'found']) {
      await page.goto(`/report/${kind}`)
      await page.getByLabel('Item name').fill(name)
      await page.getByLabel('Category', { exact: false }).selectOption('Bags')
      await page
        .getByLabel('Description')
        .fill('Navy backpack with a yellow front pocket and two straps.')
      await page.getByLabel('Campus location').selectOption('Main Library')
      await page.getByLabel('Location detail').fill('Second floor near desk 14')
      await page.getByLabel('Private identifying details').fill('Yellow zip pull and initials HX')
      if (kind === 'found') await page.getByLabel('Item handed to').selectOption('Campus Security')
      await page.getByLabel(`Date ${kind}`).fill('2026-09-25')
      await page.getByLabel('Item photo').setInputFiles(image)
      await expect(page.getByAltText('Selected photo preview')).toBeVisible()
      if (kind === 'lost')
        await page.screenshot({ path: info.outputPath('report-desktop.png'), fullPage: true })
      const createdResponse = page.waitForResponse(
        (r) =>
          new URL(r.url()).pathname === '/api/items' &&
          r.request().method() === 'POST' &&
          r.status() === 201,
      )
      await page.getByRole('button', { name: `Submit ${kind} report` }).click()
      const item = await (await createdResponse).json()
      created.push(item.id)
      await expect(
        page.getByRole('heading', {
          name: kind === 'lost' ? 'Report submitted' : 'Thanks for helping',
        }),
      ).toBeVisible()
      if (kind === 'lost') {
        await expect(page.getByRole('link', { name: 'Find possible matches' })).toHaveAttribute(
          'href',
          `/explore?view=matches&report=${item.id}`,
        )
      } else {
        await expect(page.getByRole('link', { name: 'Explore lost reports' })).toHaveAttribute(
          'href',
          '/explore?view=lost',
        )
        await expect(page.getByRole('link', { name: 'Back to home' })).toHaveAttribute('href', '/')
      }
      await expect(page.getByText('Finishing your photo upload…')).not.toBeVisible()
      const publicItem = await (await request.get(`/api/items/${item.id}`)).json()
      expect(publicItem.image_available).toBe(kind === 'lost')
      expect((await request.get(`/api/items/${item.id}/image`)).status()).toBe(
        kind === 'lost' ? 200 : 404,
      )
    }
    await page.goto(`/explore?view=matches&report=${created[0]}`)
    await expect(page.getByLabel('Lost report')).toHaveValue(String(created[0]))
    await expect(page.getByText('Advanced options')).toBeVisible()
    await expect(page.getByLabel('Matching method')).not.toBeVisible()
    await page.getByText('Advanced options').click()
    await expect(page.getByLabel('Matching method')).toHaveValue('full')
    await expect(page.getByLabel('Matching method').locator('option:checked')).toHaveText(
      'Full multimodal',
    )
    await page.getByRole('button', { name: 'Find matches', exact: true }).click()
    await expect(page.getByRole('heading', { name: 'Your potential matches' })).toBeVisible({
      timeout: 150_000,
    })
    const match = page.getByRole('article').first()
    await expect(match.getByRole('heading', { name })).toBeVisible()
    await expect(match.getByText('High Match', { exact: true })).toBeVisible()
    await expect(match.getByRole('meter', { name: 'Photo match' })).toHaveAttribute(
      'aria-valuenow',
      '100',
    )
    await page.screenshot({ path: info.outputPath('matches-desktop.png'), fullPage: true })
    await expect(match).not.toContainText('yellow front pocket')
    await match.getByRole('button', { name: 'Verify this match' }).click()
    await expect(page.getByRole('heading', { name: 'Verify this match' })).toBeVisible()
    await page.getByRole('button', { name: 'Close claim form' }).click()
    await page.goto('/explore?view=found')
    await expect(
      page
        .getByRole('navigation', { name: 'Explore sections' })
        .getByRole('link', { name: 'Found notices' }),
    ).toHaveAttribute('aria-current', 'page')
    await page.getByRole('textbox', { name: 'Search reports' }).fill(name)
    await page.getByRole('combobox', { name: 'Filter by category' }).selectOption('Bags')
    await expect(page.getByRole('article')).toHaveCount(1)
    await page.getByRole('button', { name: 'View details' }).click()
    await expect(
      page.getByText('Identifying details and the original image are kept private'),
    ).toBeVisible()
    await expect(page.getByRole('button', { name: 'Delete report', exact: true })).toHaveCount(0)
    expect((await request.get(`/api/items/${created[1]}`)).status()).toBe(200)
  } finally {
    for (const id of created) await request.delete(`/api/items/${id}`)
  }
})

test('upload failure preserves the saved report and can retry without duplication', async ({
  page,
  request,
}) => {
  let id: number | undefined
  let creates = 0
  page.on('request', (r) => {
    if (new URL(r.url()).pathname === '/api/items' && r.method() === 'POST') creates++
  })
  try {
    await page.route('**/api/items/*/image', (route) =>
      route.request().method() === 'POST'
        ? route.fulfill({
            status: 422,
            contentType: 'application/json',
            body: JSON.stringify({ detail: 'Internal debug text must not be shown' }),
          })
        : route.continue(),
    )
    await page.goto('/report/lost')
    await page.getByLabel('Item name').fill('Upload retry test')
    await page.getByLabel('Category', { exact: false }).selectOption('Bags')
    await page.getByLabel('Description').fill('A blue test backpack with yellow pocket.')
    await page.getByLabel('Campus location').selectOption('Main Library')
    await page
      .getByLabel('Item photo')
      .setInputFiles(path.resolve('../data/synthetic/images/4.png'))
    const response = page.waitForResponse(
      (r) => new URL(r.url()).pathname === '/api/items' && r.status() === 201,
    )
    await page.getByRole('button', { name: 'Submit lost report' }).click()
    id = (await (await response).json()).id
    await expect(
      page.getByText('Your report is saved, but its photo needs another try.'),
    ).toBeVisible()
    await expect(page.getByRole('alert')).not.toContainText('Internal debug')
    await page.unroute('**/api/items/*/image')
    await page.getByRole('button', { name: 'Retry photo upload' }).click()
    await expect(page.getByRole('button', { name: 'Retry photo upload' })).not.toBeVisible()
    await expect(page.getByRole('link', { name: 'Find possible matches' })).not.toHaveAttribute(
      'aria-disabled',
      'true',
    )
    expect(creates).toBe(1)
    expect((await (await request.get(`/api/items/${id}`)).json()).image_available).toBeTruthy()
  } finally {
    if (id) await request.delete(`/api/items/${id}`)
  }
})

test('friendly errors, empty states and missing-photo validation', async ({ page }) => {
  await page.route('**/api/items?*', (route) =>
    route.fulfill({ status: 500, body: 'Traceback SECRET SQL error' }),
  )
  await page.goto('/explore?view=lost')
  await expect(page.getByRole('alert')).toBeVisible()
  await expect(page.getByRole('alert')).not.toContainText('SECRET')
  await page.unroute('**/api/items?*')
  await page.getByRole('button', { name: 'Try again' }).click()
  await expect(page.getByRole('article').first()).toBeVisible()
  await page.getByRole('textbox', { name: 'Search reports' }).fill('nonexistent-unique-test-item')
  await expect(page.getByRole('heading', { name: 'No reports fit those details.' })).toBeVisible()
  await page.goto('/explore?view=matches&report=10')
  await expect(page.getByLabel('Lost report')).toHaveValue('10')
  await page.getByText('Advanced options').click()
  await page.getByLabel('Matching method').selectOption('image')
  await page.getByRole('button', { name: 'Find matches', exact: true }).click()
  await expect(page.getByRole('alert')).toContainText('Add a photo')
  await page.getByLabel('Matching method').selectOption('full')
  await page.getByRole('button', { name: 'Find matches', exact: true }).click()
  await expect(page.getByRole('heading', { name: 'Your potential matches' })).toBeVisible({
    timeout: 150_000,
  })
  await expect(page.getByRole('article').first().getByText('Unavailable or not used')).toHaveCount(
    3,
  )
})

test('main pages have no automated WCAG A/AA accessibility violations', async ({ page }) => {
  for (const url of ['/', '/report', '/report/lost', '/explore?view=lost', '/explore']) {
    await page.goto(url)
    await expect(page.getByRole('heading', { level: 1 })).toBeVisible()
    if (url.includes('view=lost')) await expect(page.getByRole('article').first()).toBeVisible()
    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
      .analyze()
    expect(
      results.violations.map((v) => ({
        page: url,
        id: v.id,
        nodes: v.nodes.map((n) => ({ target: n.target, summary: n.failureSummary })),
      })),
    ).toEqual([])
  }
  await page.getByText('Advanced options').click()
  await page.getByLabel('Matching method').selectOption('baseline')
  await page.getByRole('button', { name: 'Find matches', exact: true }).click()
  await expect(page.getByRole('heading', { name: 'Your potential matches' })).toBeVisible()
  const ranked = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
    .analyze()
  expect(
    ranked.violations.map((v) => ({
      id: v.id,
      nodes: v.nodes.map((n) => ({ target: n.target, summary: n.failureSummary })),
    })),
  ).toEqual([])
})

test('mobile explore, match results, found notices and footer do not overflow', async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 })
  const fitsViewport = async () =>
    expect(
      await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth),
    ).toBeTruthy()

  await page.goto('/report')
  await expect(page.getByRole('heading', { name: 'What happened?' })).toBeVisible()
  await fitsViewport()

  await page.goto('/explore?view=matches&report=10')
  await expect(page.getByRole('link', { name: 'Found notices' })).toBeVisible()
  await fitsViewport()
  await page.getByText('Advanced options').click()
  await expect(page.getByLabel('Matching method')).toHaveValue('full')
  await page.getByLabel('Matching method').selectOption('baseline')
  await page.getByRole('button', { name: 'Find matches', exact: true }).click()
  await expect(page.getByRole('heading', { name: 'Your potential matches' })).toBeVisible()
  await expect(
    page.getByText('Private identifying details and the original photo').first(),
  ).toBeVisible()
  await fitsViewport()

  await page.getByRole('link', { name: 'Found notices' }).click()
  await expect(page.getByText('Privacy-aware campus lost & found.')).toBeVisible()
  await expect(page.getByRole('link', { name: 'Campus staff review' })).toHaveCount(0)
  await fitsViewport()
})
