#!/usr/bin/env python3
"""
Test cases for the MBC Workload Summary feature request YAML file.

Validates that the feature request follows project standards and GitHub issue template requirements.

Author: GitHub Copilot
Issue: MBC Workload Summary Enhancements
"""

import unittest
import yaml
from pathlib import Path


class TestMBCWorkloadFeatureRequest(unittest.TestCase):
    """Test suite for MBC Workload Summary feature request YAML validation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.feature_file = Path(__file__).parent.parent / "workitems" / "features" / "mbc-workload-summary-enhancements.yml"
        self.template_file = Path(__file__).parent.parent / ".github" / "ISSUE_TEMPLATE" / "feature_request.yml"
    
    def test_feature_yaml_exists(self):
        """Test that the feature YAML file exists."""
        self.assertTrue(self.feature_file.exists(), "Feature YAML file should exist")
    
    def test_feature_yaml_valid_format(self):
        """Test that the feature YAML file has valid YAML format."""
        try:
            with open(self.feature_file) as f:
                feature_data = yaml.safe_load(f)
            self.assertIsInstance(feature_data, dict, "Feature YAML should parse to a dictionary")
        except yaml.YAMLError as e:
            self.fail(f"Feature YAML should be valid: {e}")
    
    def test_feature_required_fields(self):
        """Test that the feature YAML has all required fields."""
        with open(self.feature_file) as f:
            feature_data = yaml.safe_load(f)
        
        # Check top-level required fields
        required_top_level = ['name', 'description', 'labels', 'body']
        for field in required_top_level:
            self.assertIn(field, feature_data, f"Feature YAML should have '{field}' field")
        
        # Check that labels include expected values
        labels = feature_data.get('labels', [])
        self.assertIn('enhancement', labels, "Feature should be labeled as enhancement")
        self.assertIn('user story', labels, "Feature should be labeled as user story per project standards")
    
    def test_feature_body_structure(self):
        """Test that the feature body has the correct structure."""
        with open(self.feature_file) as f:
            feature_data = yaml.safe_load(f)
        
        body = feature_data.get('body', [])
        self.assertIsInstance(body, list, "Feature body should be a list")
        self.assertGreater(len(body), 0, "Feature body should not be empty")
        
        # Find textarea sections
        textarea_sections = [section for section in body if section.get('type') == 'textarea']
        self.assertGreaterEqual(len(textarea_sections), 3, "Should have at least 3 textarea sections")
        
        # Check for required textarea IDs
        required_ids = ['problem', 'solution', 'context']
        found_ids = [section.get('id') for section in textarea_sections if section.get('id')]
        
        for required_id in required_ids:
            self.assertIn(required_id, found_ids, f"Should have textarea section with id '{required_id}'")
    
    def test_feature_block_literal_syntax(self):
        """Test that multi-line content uses YAML block literal syntax as required by project standards."""
        with open(self.feature_file) as f:
            content = f.read()
        
        # Check for block literal syntax (|) in placeholder fields
        self.assertIn('placeholder: |', content, "Should use block literal syntax for multi-line content")
        
        # Load and check that placeholders are properly formatted
        with open(self.feature_file) as f:
            feature_data = yaml.safe_load(f)
        
        body = feature_data.get('body', [])
        for section in body:
            if section.get('type') == 'textarea':
                placeholder = section.get('attributes', {}).get('placeholder', '')
                if isinstance(placeholder, str) and len(placeholder) > 100:
                    # For long placeholders, ensure they're properly formatted
                    self.assertNotEqual(placeholder.strip(), '', "Placeholder should not be empty")
    
    def test_feature_content_quality(self):
        """Test that the feature content is comprehensive and follows project guidelines."""
        with open(self.feature_file) as f:
            feature_data = yaml.safe_load(f)
        
        # Check name and description
        name = feature_data.get('name', '')
        description = feature_data.get('description', '')
        
        self.assertIn('MBC', name, "Feature name should reference MBC (Merit Badge Counselor)")
        self.assertIn('Workload', name, "Feature name should reference workload")
        self.assertIn('Summary', name, "Feature name should reference summary")
        
        # Check that content follows project requirements
        body = feature_data.get('body', [])
        content_text = str(feature_data).lower()
        
        # Should reference key project requirements
        self.assertIn('streamlit', content_text, "Should reference Streamlit web interface")
        self.assertIn('database', content_text, "Should reference database integration")
        self.assertIn('export', content_text, "Should reference export capabilities")
        self.assertIn('filtering', content_text, "Should reference filtering capabilities")
        
        # Should follow security guidelines
        self.assertIn('pii', content_text, "Should reference PII considerations")
        self.assertIn('compliance', content_text, "Should reference compliance requirements")
    
    def test_github_template_compatibility(self):
        """Test that the feature YAML is compatible with GitHub issue template."""
        if not self.template_file.exists():
            self.skipTest("GitHub issue template not found")
        
        with open(self.template_file) as f:
            template_data = yaml.safe_load(f)
        
        with open(self.feature_file) as f:
            feature_data = yaml.safe_load(f)
        
        # Both should have body structure
        self.assertIn('body', template_data, "Template should have body")
        self.assertIn('body', feature_data, "Feature should have body")
        
        # Check that feature follows template structure
        template_body = template_data.get('body', [])
        feature_body = feature_data.get('body', [])
        
        # Template textarea sections for comparison
        template_textareas = [s for s in template_body if s.get('type') == 'textarea']
        feature_textareas = [s for s in feature_body if s.get('type') == 'textarea']
        
        self.assertGreaterEqual(len(feature_textareas), len(template_textareas), 
                               "Feature should have at least as many textarea sections as template")


if __name__ == '__main__':
    unittest.main()