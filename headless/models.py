"""Data models for headless MIDI pose cycler."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Dict, Any
from .const import (
    DEFAULT_INTERPOLATION, DEFAULT_CYCLE_MODE, DEFAULT_PRE_HOLD, 
    DEFAULT_POST_HOLD, DEFAULT_BPM, DEFAULT_BEATS_PER_BAR,
    VALID_INTERPOLATIONS, VALID_CYCLE_MODES
)


@dataclass
class ValidationResult:
    """Result of a validation check."""
    field: str
    valid: bool
    message: str
    value: Any = None


@dataclass
class FormTable:
    """Form data with validation."""
    actionNameToCreate: str
    bpm: float = DEFAULT_BPM
    beatsPerBar: int = DEFAULT_BEATS_PER_BAR
    blendFileToOutputAction: str = ""
    poseBlendFile: str = ""
    poseCatalog: str = ""
    midiFile: str = ""
    
    # Optional video fields
    shouldCreateVideo: bool = False
    audioFile: Optional[str] = None
    renderDir: Optional[str] = None
    charFile: Optional[str] = None
    
    def validate(self) -> List[ValidationResult]:
        """Validate form data."""
        results = []
        
        # Required fields
        if not self.actionNameToCreate:
            results.append(ValidationResult(
                "actionNameToCreate", False, "Action name is required"
            ))
        else:
            results.append(ValidationResult(
                "actionNameToCreate", True, "Action name provided", 
                self.actionNameToCreate
            ))
        
        # Check MIDI file exists
        if self.midiFile:
            midi_path = Path(self.midiFile)
            if midi_path.exists():
                results.append(ValidationResult(
                    "midiFile", True, "File found", self.midiFile
                ))
            else:
                results.append(ValidationResult(
                    "midiFile", False, f"File not found: {self.midiFile}"
                ))
        else:
            results.append(ValidationResult(
                "midiFile", False, "MIDI file is required"
            ))
        
        # Check pose blend file
        if self.poseBlendFile:
            pose_path = Path(self.poseBlendFile)
            if pose_path.exists():
                results.append(ValidationResult(
                    "poseBlendFile", True, "File found", self.poseBlendFile
                ))
            else:
                results.append(ValidationResult(
                    "poseBlendFile", False, f"File not found: {self.poseBlendFile}"
                ))
        else:
            results.append(ValidationResult(
                "poseBlendFile", False, "Pose blend file is required"
            ))
        
        # Validate BPM
        if self.bpm <= 0:
            results.append(ValidationResult(
                "bpm", False, f"BPM must be positive: {self.bpm}"
            ))
        else:
            results.append(ValidationResult(
                "bpm", True, f"BPM: {self.bpm}", self.bpm
            ))
        
        # Validate video settings
        if self.shouldCreateVideo:
            if self.audioFile and self.renderDir:
                audio_path = Path(self.audioFile)
                if audio_path.exists():
                    results.append(ValidationResult(
                        "audioFile", True, "Audio file found", self.audioFile
                    ))
                else:
                    results.append(ValidationResult(
                        "audioFile", False, f"Audio file not found: {self.audioFile}"
                    ))
                
                render_path = Path(self.renderDir)
                if not render_path.exists():
                    render_path.mkdir(parents=True, exist_ok=True)
                results.append(ValidationResult(
                    "renderDir", True, "Render directory ready", self.renderDir
                ))
                
                if self.charFile:
                    char_path = Path(self.charFile)
                    if char_path.exists():
                        results.append(ValidationResult(
                            "charFile", True, "Character file found", self.charFile
                        ))
                    else:
                        results.append(ValidationResult(
                            "charFile", False, f"Character file not found: {self.charFile}"
                        ))
                else:
                    results.append(ValidationResult(
                        "charFile", False, "Character file required for video"
                    ))
            else:
                if not self.audioFile:
                    results.append(ValidationResult(
                        "audioFile", False, "Audio file required when creating video"
                    ))
                if not self.renderDir:
                    results.append(ValidationResult(
                        "renderDir", False, "Render directory required when creating video"
                    ))
        
        return results


@dataclass
class DanceRow:
    """Single row of dance configuration."""
    poseCatalog: str
    track: str
    cycleMode: str = DEFAULT_CYCLE_MODE
    interpolation: str = DEFAULT_INTERPOLATION
    preHold: int = DEFAULT_PRE_HOLD
    postHold: int = DEFAULT_POST_HOLD
    
    def validate(self) -> List[ValidationResult]:
        """Validate dance row data."""
        results = []
        
        # Required fields
        if not self.poseCatalog:
            results.append(ValidationResult(
                f"poseCatalog", False, "Pose catalog is required"
            ))
        else:
            results.append(ValidationResult(
                f"poseCatalog", True, f"Catalog: {self.poseCatalog}", self.poseCatalog
            ))
        
        if not self.track:
            results.append(ValidationResult(
                f"track", False, "Track is required"
            ))
        else:
            results.append(ValidationResult(
                f"track", True, f"Track: {self.track}", self.track
            ))
        
        # Validate cycle mode
        if self.cycleMode.lower().replace(" ", "_") not in VALID_CYCLE_MODES:
            results.append(ValidationResult(
                f"cycleMode", False, 
                f"Invalid cycle mode '{self.cycleMode}'. Valid: {VALID_CYCLE_MODES}"
            ))
        else:
            results.append(ValidationResult(
                f"cycleMode", True, f"Mode: {self.cycleMode}", self.cycleMode
            ))
        
        # Validate interpolation
        if self.interpolation.lower() not in VALID_INTERPOLATIONS:
            results.append(ValidationResult(
                f"interpolation", False,
                f"Invalid interpolation '{self.interpolation}'. Valid: {VALID_INTERPOLATIONS}"
            ))
        else:
            results.append(ValidationResult(
                f"interpolation", True, f"Interpolation: {self.interpolation}", 
                self.interpolation
            ))
        
        # Validate hold frames
        if self.preHold < 0:
            results.append(ValidationResult(
                f"preHold", False, f"Pre-hold must be non-negative: {self.preHold}"
            ))
        else:
            results.append(ValidationResult(
                f"preHold", True, f"Pre-hold: {self.preHold}", self.preHold
            ))
        
        if self.postHold < 0:
            results.append(ValidationResult(
                f"postHold", False, f"Post-hold must be non-negative: {self.postHold}"
            ))
        else:
            results.append(ValidationResult(
                f"postHold", True, f"Post-hold: {self.postHold}", self.postHold
            ))
        
        return results


@dataclass
class DanceTable:
    """Dance configuration table with validation."""
    rows: List[DanceRow] = field(default_factory=list)
    
    def add_row(self, row: DanceRow):
        """Add a dance row."""
        self.rows.append(row)
    
    def validate(self) -> List[ValidationResult]:
        """Validate all dance rows."""
        results = []
        
        if not self.rows:
            results.append(ValidationResult(
                "DanceTable", False, "No dance rows defined"
            ))
            return results
        
        # Check for duplicate pose catalogs (potential bone conflicts)
        catalogs = [row.poseCatalog for row in self.rows]
        if len(catalogs) != len(set(catalogs)):
            duplicates = [c for c in catalogs if catalogs.count(c) > 1]
            results.append(ValidationResult(
                "poseCatalogs", False,
                f"Duplicate pose catalogs may cause bone conflicts: {set(duplicates)}"
            ))
        
        # Validate each row
        for i, row in enumerate(self.rows):
            row_results = row.validate()
            for result in row_results:
                result.field = f"Row {i+1} - {result.field}"
            results.extend(row_results)
        
        return results


@dataclass  
class HeadlessConfig:
    """Complete configuration for headless operation."""
    form: FormTable
    dance: DanceTable
    
    def validate(self) -> List[ValidationResult]:
        """Validate entire configuration."""
        results = []
        results.extend(self.form.validate())
        results.extend(self.dance.validate())
        return results
    
    def print_validation_table(self):
        """Print validation results as a table."""
        results = self.validate()
        
        print("\n=== Validation Results ===")
        print(f"| {'Field':<30} | {'Status':<8} | {'Message':<50} |")
        print(f"|{'-'*30}|{'-'*10}|{'-'*52}|")
        
        all_valid = True
        for result in results:
            status = "✓" if result.valid else "✗"
            if not result.valid:
                all_valid = False
            print(f"| {result.field:<30} | {status:<8} | {result.message:<50} |")
        
        print(f"\nOverall validation: {'PASSED ✓' if all_valid else 'FAILED ✗'}")
        return all_valid