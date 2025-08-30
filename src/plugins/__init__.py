# Plugin system for WhisperWriter
# Provides dynamic loading of text processors

from .base import Plugin, ProcessorPlugin

__all__ = ['Plugin', 'ProcessorPlugin']