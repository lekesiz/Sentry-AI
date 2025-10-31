"""
Project Analyzer using Manus File API.

This module analyzes project files to provide context for Claude's questions.
"""

import json
from typing import Dict, List, Optional
from pathlib import Path
from loguru import logger


class ProjectAnalyzer:
    """
    Analyze project structure and files.
    
    Uses Manus File API to read and analyze project files,
    providing context for answering Claude's questions.
    """
    
    def __init__(self, project_path: str):
        """
        Initialize the project analyzer.
        
        Args:
            project_path: Path to the project directory
        """
        self.project_path = Path(project_path)
        logger.info(f"Project analyzer initialized: {project_path}")
    
    def analyze(self) -> Dict[str, any]:
        """
        Analyze the entire project.
        
        Returns:
            Dictionary with project analysis results
        """
        logger.info("Starting project analysis...")
        
        analysis = {
            'path': str(self.project_path),
            'type': self._detect_project_type(),
            'dependencies': self._analyze_dependencies(),
            'database': self._analyze_database(),
            'api': self._analyze_api(),
            'environment': self._analyze_environment(),
            'structure': self._analyze_structure()
        }
        
        logger.info(f"Project analysis complete: {analysis['type']}")
        return analysis
    
    def _detect_project_type(self) -> str:
        """
        Detect the type of project.
        
        Returns:
            Project type (e.g., 'node', 'python', 'unknown')
        """
        # Check for common project files
        if (self.project_path / 'package.json').exists():
            return 'node'
        elif (self.project_path / 'requirements.txt').exists():
            return 'python'
        elif (self.project_path / 'Cargo.toml').exists():
            return 'rust'
        elif (self.project_path / 'go.mod').exists():
            return 'go'
        else:
            return 'unknown'
    
    def _analyze_dependencies(self) -> Dict[str, List[str]]:
        """
        Analyze project dependencies.
        
        Returns:
            Dictionary with dependency information
        """
        dependencies = {}
        
        try:
            # Node.js project
            pkg_json = self.project_path / 'package.json'
            if pkg_json.exists():
                # In production, use Manus File API:
                # from manus_tools import file
                # content = file(path=str(pkg_json), action="read")
                
                with open(pkg_json, 'r') as f:
                    data = json.load(f)
                    dependencies['runtime'] = list(data.get('dependencies', {}).keys())
                    dependencies['dev'] = list(data.get('devDependencies', {}).keys())
            
            # Python project
            requirements = self.project_path / 'requirements.txt'
            if requirements.exists():
                with open(requirements, 'r') as f:
                    deps = [line.split('==')[0].strip() for line in f if line.strip() and not line.startswith('#')]
                    dependencies['python'] = deps
        
        except Exception as e:
            logger.error(f"Error analyzing dependencies: {e}")
        
        return dependencies
    
    def _analyze_database(self) -> Dict[str, any]:
        """
        Analyze database configuration and schema.
        
        Returns:
            Dictionary with database information
        """
        database_info = {}
        
        try:
            # Check for Prisma schema
            prisma_schema = self._find_file('**/*.prisma')
            if prisma_schema:
                database_info['type'] = 'prisma'
                database_info['schema_file'] = prisma_schema
                database_info['models'] = self._parse_prisma_models(prisma_schema)
            
            # Check for Sequelize
            elif self._find_file('**/models/index.js'):
                database_info['type'] = 'sequelize'
            
            # Check for Django
            elif self._find_file('**/models.py'):
                database_info['type'] = 'django'
        
        except Exception as e:
            logger.error(f"Error analyzing database: {e}")
        
        return database_info
    
    def _analyze_api(self) -> Dict[str, any]:
        """
        Analyze API structure and endpoints.
        
        Returns:
            Dictionary with API information
        """
        api_info = {}
        
        try:
            # Check for Express.js
            if self._find_file('**/routes/**/*.js'):
                api_info['framework'] = 'express'
                api_info['routes'] = self._find_files('**/routes/**/*.js')
            
            # Check for FastAPI
            elif self._find_file('**/api/**/*.py'):
                api_info['framework'] = 'fastapi'
                api_info['routes'] = self._find_files('**/api/**/*.py')
            
            # Check for Next.js API routes
            elif self._find_file('**/pages/api/**/*.js'):
                api_info['framework'] = 'nextjs'
                api_info['routes'] = self._find_files('**/pages/api/**/*.js')
        
        except Exception as e:
            logger.error(f"Error analyzing API: {e}")
        
        return api_info
    
    def _analyze_environment(self) -> Dict[str, List[str]]:
        """
        Analyze environment variables.
        
        Returns:
            Dictionary with environment variable names
        """
        env_vars = {}
        
        try:
            # Check .env.example
            env_example = self.project_path / '.env.example'
            if env_example.exists():
                with open(env_example, 'r') as f:
                    vars = [line.split('=')[0].strip() for line in f if '=' in line and not line.startswith('#')]
                    env_vars['required'] = vars
            
            # Check .env
            env_file = self.project_path / '.env'
            if env_file.exists():
                with open(env_file, 'r') as f:
                    vars = [line.split('=')[0].strip() for line in f if '=' in line and not line.startswith('#')]
                    env_vars['configured'] = vars
        
        except Exception as e:
            logger.error(f"Error analyzing environment: {e}")
        
        return env_vars
    
    def _analyze_structure(self) -> Dict[str, int]:
        """
        Analyze project structure.
        
        Returns:
            Dictionary with structure statistics
        """
        structure = {
            'total_files': 0,
            'source_files': 0,
            'test_files': 0,
            'config_files': 0
        }
        
        try:
            for file_path in self.project_path.rglob('*'):
                if file_path.is_file():
                    structure['total_files'] += 1
                    
                    # Categorize files
                    if file_path.suffix in ['.js', '.ts', '.py', '.go', '.rs']:
                        if 'test' in file_path.name or 'spec' in file_path.name:
                            structure['test_files'] += 1
                        else:
                            structure['source_files'] += 1
                    elif file_path.suffix in ['.json', '.yaml', '.yml', '.toml']:
                        structure['config_files'] += 1
        
        except Exception as e:
            logger.error(f"Error analyzing structure: {e}")
        
        return structure
    
    def _find_file(self, pattern: str) -> Optional[str]:
        """
        Find a file matching the pattern.
        
        Args:
            pattern: Glob pattern to match
            
        Returns:
            Path to the first matching file, or None
        """
        try:
            # In production, use Manus Match API:
            # from manus_tools import match
            # results = match(scope=f"{self.project_path}/{pattern}", action="glob")
            # return results[0] if results else None
            
            matches = list(self.project_path.glob(pattern))
            return str(matches[0]) if matches else None
        
        except Exception as e:
            logger.error(f"Error finding file: {e}")
            return None
    
    def _find_files(self, pattern: str) -> List[str]:
        """
        Find all files matching the pattern.
        
        Args:
            pattern: Glob pattern to match
            
        Returns:
            List of matching file paths
        """
        try:
            matches = list(self.project_path.glob(pattern))
            return [str(m) for m in matches]
        
        except Exception as e:
            logger.error(f"Error finding files: {e}")
            return []
    
    def _parse_prisma_models(self, schema_file: str) -> List[str]:
        """
        Parse Prisma schema to extract model names.
        
        Args:
            schema_file: Path to Prisma schema file
            
        Returns:
            List of model names
        """
        models = []
        
        try:
            with open(schema_file, 'r') as f:
                for line in f:
                    if line.strip().startswith('model '):
                        model_name = line.strip().split()[1]
                        models.append(model_name)
        
        except Exception as e:
            logger.error(f"Error parsing Prisma models: {e}")
        
        return models
    
    def get_summary(self) -> str:
        """
        Get a human-readable summary of the project.
        
        Returns:
            Summary string
        """
        analysis = self.analyze()
        
        summary_parts = [
            f"Project Type: {analysis['type']}",
        ]
        
        # Dependencies
        if analysis['dependencies']:
            deps = analysis['dependencies']
            if 'runtime' in deps:
                summary_parts.append(f"Runtime Dependencies: {len(deps['runtime'])}")
            if 'dev' in deps:
                summary_parts.append(f"Dev Dependencies: {len(deps['dev'])}")
        
        # Database
        if analysis['database']:
            db = analysis['database']
            summary_parts.append(f"Database: {db.get('type', 'unknown')}")
            if 'models' in db:
                summary_parts.append(f"Models: {', '.join(db['models'][:5])}")
        
        # API
        if analysis['api']:
            api = analysis['api']
            summary_parts.append(f"API Framework: {api.get('framework', 'unknown')}")
        
        # Structure
        if analysis['structure']:
            struct = analysis['structure']
            summary_parts.append(f"Source Files: {struct.get('source_files', 0)}")
            summary_parts.append(f"Test Files: {struct.get('test_files', 0)}")
        
        return "\n".join(summary_parts)


# Helper functions

def analyze_project(project_path: str) -> Dict[str, any]:
    """
    Analyze a project and return results.
    
    Args:
        project_path: Path to the project directory
        
    Returns:
        Dictionary with analysis results
    """
    analyzer = ProjectAnalyzer(project_path)
    return analyzer.analyze()


def get_project_summary(project_path: str) -> str:
    """
    Get a human-readable project summary.
    
    Args:
        project_path: Path to the project directory
        
    Returns:
        Summary string
    """
    analyzer = ProjectAnalyzer(project_path)
    return analyzer.get_summary()
