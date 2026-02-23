import simpleGit from 'simple-git';
import { spawn } from 'child_process';

const git = simpleGit();

/**
 * Check if there are any staged files
 * @returns {Promise<boolean>}
 */
export async function hasStagedFiles() {
  try {
    const status = await git.status();
    return status.staged.length > 0;
  } catch (error) {
    throw new Error(`Failed to check git status: ${error.message}`);
  }
}

/**
 * Get the diff of staged files
 * @returns {Promise<string>}
 */
export async function getStagedDiff() {
  try {
    const diff = await git.diff(['--cached']);
    return diff;
  } catch (error) {
    throw new Error(`Failed to get staged diff: ${error.message}`);
  }
}

/**
 * Create a commit with title and body
 * @param {string} title - Commit title
 * @param {string} body - Commit body
 * @returns {Promise<void>}
 */
export async function commitWithMessage(title, body) {
  try {
    await git.commit([title, body]);
  } catch (error) {
    throw new Error(`Failed to create commit: ${error.message}`);
  }
}

/**
 * Passthrough command directly to git
 * @param {string[]} args - Command arguments
 * @returns {Promise<void>}
 */
export async function passthroughToGit(args) {
  return new Promise((resolve, reject) => {
    const gitProcess = spawn('git', args, {
      stdio: 'inherit',
      shell: true
    });

    gitProcess.on('close', (code) => {
      if (code === 0) {
        resolve();
      } else {
        process.exit(code);
      }
    });

    gitProcess.on('error', (error) => {
      reject(new Error(`Failed to execute git command: ${error.message}`));
    });
  });
}
