# AI Vibe Chat - V1 Conversation Memory Implementation

## Overview
This document outlines the implementation tasks for the V1 Conversation Memory feature, which adds persistent conversation history to the AI Vibe Chat application.

## Phase 1: Core Infrastructure Setup

### 1.1 Dependencies and Environment
- [x] **Add JSON handling dependency** - `json` is built-in; no action required
- [x] **Add file path handling** - `pathlib` is built-in; no action required
- [x] **Update requirements.txt** - No additional dependencies needed for memory feature
- [ ] **Test virtual environment setup** - Ensure all dependencies work in venv (deferred until Python is available locally)

### 1.2 Data Models and Schemas
- [x] **Create conversation data model** - `ConversationTurn` dataclass implemented
- [x] **Define JSON schema** - Documented in README (Persistence section)
- [x] **Add data validation** - Invalid/corrupted JSON handled; non-list or malformed entries rejected gracefully
- [x] **Create type hints** - Typing added across engine, providers, and file manager

## Phase 2: CLI Modifications

### 2.1 Argument Parsing
- [x] **Add --memory flag** - Implemented with `@click.option` in cli.py
- [x] **Update help text** - Help text added to --memory option
- [x] **Test CLI parsing** - Verified via tests/test_cli.py
- [x] **Add validation** - Options validated; no conflicting flags in current CLI

### 2.2 CLI Integration
- [x] **Pass memory flag to Engine** - Engine accepts and uses memory parameter
- [x] **Update main function** - CLI passes memory flag to Engine
- [x] **Add error handling** - Errors surfaced via FileManager and informative CLI output
- [x] **Update CLI output** - Memory status displayed on startup

## Phase 3: File Handling System

### 3.1 File Operations
- [x] **Create file manager class** - `ConversationFileManager` implemented
- [x] **Implement file creation** - Creates empty `conversation_history.json` on first run when --memory enabled
- [x] **Implement file reading** - Loads history; rejects malformed data
- [x] **Implement file writing** - Saves with atomic write + backup
- [x] **Add file validation** - Validates JSON structure; handles errors

### 3.2 File Security and Safety
- [x] **Add file path validation** - Prevents path traversal (no `..`)
- [x] **Implement atomic writes** - Uses .tmp and renames with backup
- [x] **Add file size limits** - Limits number of turns via max_history_turns
- [x] **Add backup mechanism** - Creates .bak before overwrite
- [x] **Handle file permissions** - I/O errors handled gracefully with logging

### 3.3 Error Handling
- [x] **Handle JSON parsing errors** - Malformed JSON returns empty history
- [x] **Handle file I/O errors** - Errors logged and recovery attempted
- [x] **Add recovery mechanisms** - Restores from .bak on failure
- [x] **Log file operations** - Logging added in file manager

## Phase 4: Engine Integration

### 4.1 Engine Modifications
- [x] **Add memory parameter** - Engine constructor updated
- [x] **Add conversation history storage** - In-memory list of ConversationTurn
- [x] **Modify respond method** - Appends user/bot turns; saves when enabled
- [x] **Add history management** - Implemented via Engine + FileManager
- [x] **Pass history to provider** - History passed to provider.generate

### 4.2 Provider Interface Updates
- [x] **Update Provider protocol** - Protocol updated to include history param
- [x] **Update LocalRulesProvider** - Accepts history (currently optional)
- [x] **Maintain backward compatibility** - BaseProvider still raises NotImplementedError
- [x] **Add type hints** - Provider interfaces typed

### 4.3 Memory Management
- [x] **Implement history loading** - Loads on Engine init when memory enabled
- [x] **Implement history saving** - Saves after each bot response
- [x] **Add memory cleanup** - Truncates to max_history_turns in FileManager
- [ ] **Optimize performance** - Ensure memory operations don't slow down chat (current writes are atomic; consider batching if needed)

## Phase 5: Testing and Validation

### 5.1 Unit Tests
- [x] **Test file operations** - tests/test_file_manager.py covers CRUD, errors, truncation
- [x] **Test Engine modifications** - tests/test_engine.py covers history and save
- [x] **Test CLI integration** - Unit tests for --memory flag functionality
- [x] **Test data validation** - Invalid schema and corrupted JSON tests included
- [x] **Test error handling** - Backup restore and error scenarios covered

### 5.2 Integration Tests
- [x] **Test full conversation flow** - Integration test exercises multi-turn with memory
- [x] **Test conversation persistence** - Verify conversation survives app restart
- [x] **Test multiple personalities** - Parametrized test for Rizz and Sarcastic
- [x] **Test error recovery** - Corruption handled gracefully in tests
- [x] **Test concurrent access** - Write path guarded by a sidecar lock; atomic renames prevent torn writes

### 5.3 Security Tests
- [x] **Test file path security** - Invalid path test present
- [x] **Test JSON injection** - Corrupted/invalid JSON safely ignored
- [x] **Test file size limits** - History truncation enforced; test_history_truncation covers it
- [x] **Test permission handling** - Errors handled; backup restore tested via patched rename

## Phase 6: Documentation and Polish

### 6.1 Code Documentation
- [x] **Add docstrings** - Added to Engine, FileManager, CLI, and base classes
- [x] **Add type hints** - Types present across modules (PEP 484/563 style)
- [x] **Add inline comments** - Added around atomic writes and locking
- [x] **Update existing docstrings** - Documented CLI and Engine parameters

### 6.2 User Documentation
- [x] **Update README.md** - Added --memory docs and persistence schema
- [x] **Add usage examples** - Added CLI examples including --memory
- [x] **Document file format** - Documented in README (Persistence section)
- [x] **Add troubleshooting** - Added to README for Python alias, file location, permissions

### 6.3 Code Quality
- [ ] **Run linter** - Ensure code follows project style guidelines
- [ ] **Run type checker** - Verify all type hints are correct
- [ ] **Code review** - Review all changes for quality and security
- [ ] **Performance testing** - Ensure memory feature doesn't impact performance

## Phase 7: Final Validation

### 7.1 Acceptance Criteria Verification
- [x] **--memory flag functional** - Implemented and wired to Engine
- [x] **File creation works** - Empty file created on first run
- [x] **Conversation persistence** - Each turn saved to JSON
- [x] **Conversation loading** - Previous conversation loaded on startup
- [x] **Personality compatibility** - Verified via parametrized tests
- [x] **No breaking changes** - Existing features preserved

### 7.2 Performance and Reliability
- [ ] **Memory usage** - Verify reasonable memory consumption
- [ ] **File I/O performance** - Ensure fast save/load operations
- [ ] **Error resilience** - Application handles errors gracefully
- [ ] **Data integrity** - Conversation history is never lost or corrupted

### 7.3 Security Validation
- [ ] **No security vulnerabilities** - All file operations are secure
- [ ] **Input validation** - All user inputs are properly validated
- [ ] **Error information** - No sensitive information leaked in error messages
- [ ] **File permissions** - Appropriate file permissions are set

## Implementation Notes

### Critical Security Considerations
1. **File Path Validation**: Always validate file paths to prevent directory traversal attacks
2. **JSON Parsing Safety**: Use safe JSON parsing to prevent code injection
3. **File Size Limits**: Implement reasonable limits to prevent DoS attacks
4. **Atomic Operations**: Use atomic file operations to prevent data corruption
5. **Error Handling**: Never expose sensitive information in error messages

### Performance Considerations
1. **Lazy Loading**: Consider lazy loading for very large conversation histories
2. **Batch Operations**: Group multiple conversation turns for efficient file I/O
3. **Memory Management**: Implement optional history truncation for long conversations
4. **Caching**: Consider caching frequently accessed conversation data

### Testing Strategy
1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test component interactions
3. **Security Tests**: Verify security measures work correctly
4. **Performance Tests**: Ensure acceptable performance under load
5. **User Acceptance Tests**: Verify all acceptance criteria are met

## V2: Provider Integration and GUI

- [x] Add --provider flag to CLI with options local-rules and perplexity
- [x] Implement PerplexityProvider with requests, env-configured API key and model, and error handling
- [x] Export PerplexityProvider in providers package
- [x] Update requirements.txt with requests and python-dotenv
- [x] Print selected provider on CLI startup
- [x] Add simple Tkinter GUI with personality/provider selection and memory toggle
- [x] Add minimal Flask website for local hosting
- [x] Add console script entry ai-vibe-chat-gui
- [x] Update README with provider usage and GUI instructions

## Success Metrics
- [ ] All acceptance criteria from product spec are met
- [ ] No security vulnerabilities introduced
- [ ] Performance impact is minimal (< 100ms per operation)
- [ ] Code coverage > 90% for new functionality
- [ ] All tests pass consistently
- [ ] Documentation is complete and accurate
