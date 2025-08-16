# TODO - MIDI Pose Cycler Extension

## Pre-Release Checklist
- [x] Update version to development format (0.x.x)
- [x] Add proper extension tags (Animation, User Interface)
- [x] Bundle mido library in vendor/ directory
- [x] Ensure no external dependencies or pip installations
- [x] Add Blender Extension Guidelines compliance section to docs
- [ ] Test on fresh Blender 4.5 installation
- [ ] Test read-only "System" installation support
- [ ] Verify no hardcoded paths or device-specific code

## Testing Requirements
- [ ] Test with various MIDI file formats
- [ ] Test with empty/invalid MIDI files
- [ ] Test error handling for missing poses
- [ ] Test with different FPS settings
- [ ] Test with large MIDI files (performance)
- [ ] Test undo/redo functionality
- [ ] Test with multiple objects selected

## Documentation
- [ ] Add user guide with screenshots
- [ ] Create example MIDI files for testing
- [ ] Document known limitations
- [ ] Add troubleshooting for common issues

## Future Features (Post-Release)
- [ ] Add preview functionality before rendering
- [ ] Support for MIDI tempo changes
- [ ] Visual timeline for MIDI notes
- [ ] Batch processing for multiple MIDI tracks
- [ ] Export animation presets
- [ ] Support for CC (Control Change) messages
- [ ] Add pose blending options

## Code Quality
- [ ] Add type hints to all functions
- [ ] Add docstrings to all public functions
- [ ] Consider PEP 8 compliance check
- [ ] Add unit tests for MIDI parsing functions

## Publishing
- [ ] Create extension icon/thumbnail
- [ ] Write compelling extension description
- [ ] Prepare demo video/GIF
- [ ] Submit to Blender Extensions platform
- [ ] Set up issue tracker for user feedback

## Known Issues
- None currently identified

## Notes
- Extension is currently in development (v0.1.0)
- All critical compliance issues have been addressed
- Mido library is properly bundled to avoid external dependencies