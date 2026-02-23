#!/usr/bin/env node

import { Command } from 'commander';
import * as clack from '@clack/prompts';
import pc from 'picocolors';
import { hasStagedFiles, getStagedDiff, commitWithMessage, passthroughToGit } from './git.js';
import { generateConventionalCommit } from './lingo.js';

const program = new Command();

program
  .name('lit')
  .description('Type how you think, commit effortlessly')
  .version('1.0.0')
  .allowUnknownOption()
  .allowExcessArguments();

// Special handling for commit command with -m flag
program
  .command('commit')
  .allowUnknownOption()
  .allowExcessArguments()
  .action(async (options, command) => {
    const args = process.argv.slice(3);
    
    // Check if -m flag is present
    const messageIndex = args.findIndex(arg => arg === '-m' || arg === '--message');
    
    if (messageIndex === -1) {
      // No -m flag, passthrough to git
      await passthroughToGit(['commit', ...args]);
      return;
    }

    // Extract raw message
    const rawMessage = args[messageIndex + 1];
    
    if (!rawMessage) {
      clack.log.error(pc.red('Error: -m flag requires a message'));
      process.exit(1);
    }

    try {
      // Check for staged files
      const hasStaged = await hasStagedFiles();
      
      if (!hasStaged) {
        clack.log.error(pc.red('No staged files found. Use git add to stage files first.'));
        process.exit(1);
      }

      // Get staged diff
      const diff = await getStagedDiff();
      
      if (!diff || diff.trim().length === 0) {
        clack.log.error(pc.red('Empty diff. Nothing to commit.'));
        process.exit(1);
      }

      // Show spinner while translating
      const spinner = clack.spinner();
      spinner.start('Translating and analyzing diff via Lingo.dev...');

      // Generate conventional commit
      const result = await generateConventionalCommit(rawMessage, diff);
      
      spinner.stop('Translation complete');

      // Display preview
      console.log('\n' + pc.cyan('Generated commit:'));
      console.log(pc.bold(result.title));
      console.log();
      console.log(pc.dim(result.body));
      console.log();

      // Prompt user
      const action = await clack.select({
        message: 'What would you like to do?',
        options: [
          { value: 'accept', label: 'Accept' },
          { value: 'edit', label: 'Edit manually' },
          { value: 'cancel', label: 'Cancel' }
        ]
      });

      if (clack.isCancel(action) || action === 'cancel') {
        clack.log.info('Commit cancelled');
        process.exit(0);
      }

      let finalTitle = result.title;
      let finalBody = result.body;

      if (action === 'edit') {
        finalTitle = await clack.text({
          message: 'Commit title:',
          placeholder: result.title,
          defaultValue: result.title,
          validate: (value) => {
            if (!value) return 'Title is required';
            if (value.length > 72) return 'Title should be under 72 characters';
          }
        });

        if (clack.isCancel(finalTitle)) {
          clack.log.info('Commit cancelled');
          process.exit(0);
        }

        finalBody = await clack.text({
          message: 'Commit body:',
          placeholder: result.body,
          defaultValue: result.body
        });

        if (clack.isCancel(finalBody)) {
          clack.log.info('Commit cancelled');
          process.exit(0);
        }
      }

      // Commit
      await commitWithMessage(finalTitle, finalBody);
      clack.log.success(pc.green('Commit created successfully!'));

    } catch (error) {
      clack.log.error(pc.red(`Error: ${error.message}`));
      process.exit(1);
    }
  });

// Handle all other commands - passthrough to git
program
  .action(async () => {
    const args = process.argv.slice(2);
    
    if (args.length === 0) {
      // No arguments, show help
      program.help();
      return;
    }

    // Passthrough to git
    await passthroughToGit(args);
  });

program.parse();

/*
USAGE EXAMPLES:

# Normal git commands (proxied)
lit status
lit add .
lit push origin main
lit checkout -b feature/new-feature
lit log --oneline
lit branch
lit pull

# AI-powered commit (special handling)
lit commit -m "login bug fix aur validation add kiya"
lit commit -m "isse bara number ka issue fix ho jata hai"
lit commit -m "added new user dashboard with charts"

# Regular commit without -m (proxied to git)
lit commit
lit commit --amend

# Expected AI translation flow:
Input: "login bug fix aur validation add kiya"
Output:
  fix: correct login validation logic
  
  - add required field checks
  - resolve authentication flow issue

*/
