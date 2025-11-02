## Context
The current implementation hardcodes model capability checks, specifically for speed support. This creates maintenance burden when ElevenLabs adds new models or extends capabilities. We need a flexible system that can adapt to changes without requiring code updates in multiple places.

## Goals / Non-Goals

### Goals
- Dynamic detection of model capabilities (especially speed support)
- Single source of truth for model capabilities
- UI automatically adapts to model selection
- Easy to extend for future capabilities (style, other settings)
- Backward compatible with existing models
- Performance optimized with caching

### Non-Goals
- Real-time API calls to determine capabilities (will use allow-list/pattern matching)
- Complex capability negotiation with ElevenLabs API
- Changing existing model behavior or breaking changes

## Decisions

### Decision: Allow-List with Pattern Matching Fallback
**What**: Use an allow-list of model IDs that support speed, with pattern matching as fallback for unknown models.

**Why**: 
- ElevenLabs API doesn't explicitly expose capability flags
- Pattern matching (e.g., "multilingual" in model name) provides reasonable defaults
- Allow-list ensures explicit control for known models
- Easy to maintain and extend

**Alternatives considered**:
- Pattern-only: Less reliable, might misclassify models
- Full allow-list only: Requires manual updates for every new model
- API-based detection: ElevenLabs API doesn't provide this information

### Decision: Utility Module for Capabilities
**What**: Create `utils/model_capabilities.py` module with capability detection functions.

**Why**:
- Centralizes capability logic
- Easy to test in isolation
- Can be reused across UI and validation code
- Clear separation of concerns

**Alternatives considered**:
- Inline in Elevenlabs_functions.py: Would clutter core functions
- Configuration file: Overkill for current needs, can add later if needed

### Decision: Caching Capability Results
**What**: Use `@st_cache` decorator to cache capability detection results.

**Why**:
- Model capabilities don't change during a session
- Reduces redundant pattern matching/allow-list lookups
- Improves UI responsiveness

**Alternatives considered**:
- No caching: Unnecessary overhead for simple checks
- Manual caching: `@st_cache` is simpler and follows project patterns

## Implementation Approach

### Phase 1: Core Capability System
1. Create `utils/model_capabilities.py`
2. Implement `supports_speed()` with allow-list + pattern matching
3. Add caching decorator

### Phase 2: Update Validation
1. Replace hardcoded checks in `generate_audio()`
2. Update error messages to be dynamic
3. Update `bulk_generate_audio()`

### Phase 3: Update UI
1. Update `app.py` to use capability checks
2. Update `pages/Bulk_Generation.py` to use capability checks
3. Make help text dynamic

### Phase 4: Testing & Documentation
1. Add comprehensive tests
2. Update existing tests
3. Update documentation

## Risks / Trade-offs

### Risk: Pattern Matching May Misclassify Models
**Mitigation**: Use conservative patterns, prefer allow-list for certainty. Can be adjusted based on actual model names.

### Risk: Maintenance Overhead for Allow-List
**Mitigation**: Start with known models, add new ones as needed. Pattern matching reduces need for exhaustive list.

### Trade-off: Flexibility vs Performance
**Decision**: Pattern matching provides flexibility, caching provides performance. Good balance.

## Migration Plan

1. **Additive Changes**: New capability system doesn't break existing code
2. **Gradual Rollout**: Update validation first, then UI
3. **Backward Compatibility**: Existing models continue to work with same behavior
4. **Testing**: Comprehensive tests ensure no regressions

## Open Questions

- Should we support user-configurable allow-list? (Future enhancement)
- Should we add capability detection for other settings (style, etc.) now or later? (Start with speed, extend later)
- Should we log capability detection misses for monitoring? (Consider for production)

