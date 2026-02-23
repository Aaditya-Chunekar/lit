/**
 * Generate conventional commit message using Lingo API
 * @param {string} rawMessage - User's raw commit message
 * @param {string} diff - Git diff of staged changes
 * @returns {Promise<{title: string, body: string}>}
 */
export async function generateConventionalCommit(rawMessage, diff) {
  const apiUrl = process.env.LINGO_API_URL;
  const apiKey = process.env.LINGO_API_KEY;

  // Validate environment variables
  if (!apiUrl || !apiKey) {
    console.warn('Warning: LINGO_API_URL or LINGO_API_KEY not set. Using fallback.');
    return fallbackCommitGeneration(rawMessage, diff);
  }

  const systemPrompt = `Detect the source language. It may be a mixed colloquial language like Hinglish (e.g., 'isse bara number ka issue fix ho jata hai'). Translate the intent to standard English. Analyze the provided git diff. Output a standard Conventional Commit with:
- a short, lowercase type (feat, fix, refactor, docs, chore, test, perf)
- a concise title under 72 characters
- a short body explaining what changed and why.
Return JSON:
{
  title: string,
  body: string
}`;

  const payload = {
    systemPrompt,
    rawMessage,
    diff: diff.substring(0, 4000) // Limit diff size to avoid payload issues
  };

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 15000); // 15 second timeout

    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      },
      body: JSON.stringify(payload),
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`API returned status ${response.status}`);
    }

    const data = await response.json();

    // Validate response structure
    if (!data.title || !data.body) {
      throw new Error('Invalid API response format');
    }

    return {
      title: data.title,
      body: data.body
    };

  } catch (error) {
    if (error.name === 'AbortError') {
      console.warn('Warning: API request timed out. Using fallback.');
    } else {
      console.warn(`Warning: API error (${error.message}). Using fallback.`);
    }
    
    return fallbackCommitGeneration(rawMessage, diff);
  }
}

/**
 * Fallback commit generation using heuristics
 * @param {string} rawMessage - User's raw commit message
 * @param {string} diff - Git diff of staged changes
 * @returns {{title: string, body: string}}
 */
function fallbackCommitGeneration(rawMessage, diff) {
  // Clean and normalize the message
  const cleanMessage = rawMessage.trim();
  
  // Detect commit type based on keywords and diff
  const type = detectCommitType(cleanMessage, diff);
  
  // Create title (lowercase, concise)
  const title = `${type}: ${cleanMessage.toLowerCase().substring(0, 60)}`;
  
  // Generate simple body
  const body = generateBodyFromDiff(diff);
  
  return { title, body };
}

/**
 * Detect commit type from message and diff
 * @param {string} message - Commit message
 * @param {string} diff - Git diff
 * @returns {string}
 */
function detectCommitType(message, diff) {
  const lowerMessage = message.toLowerCase();
  
  // Keyword-based detection
  if (lowerMessage.match(/\b(add|new|create|added|created)\b/)) {
    return 'feat';
  }
  if (lowerMessage.match(/\b(fix|bug|resolve|patch|correct)\b/)) {
    return 'fix';
  }
  if (lowerMessage.match(/\b(refactor|restructure|rewrite|cleanup)\b/)) {
    return 'refactor';
  }
  if (lowerMessage.match(/\b(doc|readme|comment|documentation)\b/)) {
    return 'docs';
  }
  if (lowerMessage.match(/\b(test|spec|testing)\b/)) {
    return 'test';
  }
  if (lowerMessage.match(/\b(perf|performance|optimize|speed)\b/)) {
    return 'perf';
  }
  if (lowerMessage.match(/\b(style|format|lint)\b/)) {
    return 'style';
  }
  
  // Diff-based detection
  if (diff.includes('test/') || diff.includes('.test.') || diff.includes('.spec.')) {
    return 'test';
  }
  if (diff.includes('README') || diff.includes('.md')) {
    return 'docs';
  }
  
  // Check if mostly additions (new feature)
  const additions = (diff.match(/^\+[^+]/gm) || []).length;
  const deletions = (diff.match(/^-[^-]/gm) || []).length;
  
  if (additions > deletions * 2) {
    return 'feat';
  }
  
  // Default to fix if unsure
  return 'fix';
}

/**
 * Generate commit body from diff analysis
 * @param {string} diff - Git diff
 * @returns {string}
 */
function generateBodyFromDiff(diff) {
  const lines = diff.split('\n');
  const filesChanged = [];
  
  for (const line of lines) {
    if (line.startsWith('diff --git')) {
      const match = line.match(/b\/(.*)/);
      if (match) {
        filesChanged.push(match[1]);
      }
    }
  }
  
  if (filesChanged.length === 0) {
    return 'Update implementation';
  }
  
  if (filesChanged.length === 1) {
    return `Update ${filesChanged[0]}`;
  }
  
  return `Update multiple files:\n${filesChanged.slice(0, 5).map(f => `- ${f}`).join('\n')}`;
}
