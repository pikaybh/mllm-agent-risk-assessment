from abc import ABC, abstractmethod
from typing import Any, Optional, Type

from embedchain.models.data_type import DataType
from pydantic import BaseModel, Field, model_validator

from crewai_tools.tools.base_tool import BaseTool


class Adapter(BaseModel, ABC):
    class Config:
        arbitrary_types_allowed = True

    @abstractmethod
    def query(self, question: str) -> str:
        """Query the knowledge base with a question and return the answer."""

    @abstractmethod
    def add(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Add content to the knowledge base."""



class RagTool(BaseTool):
    class _AdapterPlaceholder(Adapter):
        def query(self, question: str) -> str:
            raise NotImplementedError

        def add(self, *args: Any, **kwargs: Any) -> None:
            raise NotImplementedError

    name: str = "Knowledge base"
    description: str = "A knowledge base that can be used to answer questions."
    summarize: bool = False
    adapter: Adapter = Field(default_factory=_AdapterPlaceholder)
    config: dict[str, Any] | None = None

    @model_validator(mode="after")
    def _set_default_adapter(self):
        if isinstance(self.adapter, RagTool._AdapterPlaceholder):
            from embedchain import App

            from crewai_tools.adapters.embedchain_adapter import EmbedchainAdapter

            app = App.from_config(config=self.config) if self.config else App()
            self.adapter = EmbedchainAdapter(
                embedchain_app=app, summarize=self.summarize
            )

        return self

    def add(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.adapter.add(*args, **kwargs)

    def _run(
        self,
        query: str,
        **kwargs: Any,
    ) -> Any:
        self._before_run(query, **kwargs)

        return f"Relevant Content:\n{self.adapter.query(query)}"

    def _before_run(self, query, **kwargs):
        pass



class FixedPDFSearchToolSchema(BaseModel):
    """Input for PDFSearchTool."""

    query: str = Field(
        ..., description="Mandatory query you want to use to search the PDF's content"
    )



class PDFSearchToolSchema(FixedPDFSearchToolSchema):
    """Input for PDFSearchTool."""

    pdf: str = Field(..., description="Mandatory pdf path you want to search")



class PDFSearchTool(RagTool):
    name: str = "Search a PDF's content"
    description: str = (
        "A tool that can be used to semantic search a query from a PDF's content."
    )
    args_schema: Type[BaseModel] = PDFSearchToolSchema

    def __init__(self, pdf: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        if pdf is not None:
            kwargs["data_type"] = DataType.PDF_FILE
            self.add(pdf)
            self.description = f"A tool that can be used to semantic search a query the {pdf} PDF's content."
            self.args_schema = FixedPDFSearchToolSchema
            self._generate_description()

    @model_validator(mode="after")
    def _set_default_adapter(self):
        if isinstance(self.adapter, RagTool._AdapterPlaceholder):
            from embedchain import App

            from crewai_tools.adapters.pdf_embedchain_adapter import (
                PDFEmbedchainAdapter,
            )

            app = App.from_config(config=self.config) if self.config else App()
            self.adapter = PDFEmbedchainAdapter(
                embedchain_app=app, summarize=self.summarize
            )

        return self

    def add(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().add(*args, **kwargs)

    def _before_run(
        self,
        query: str,
        **kwargs: Any,
    ) -> Any:
        if "pdf" in kwargs:
            self.add(kwargs["pdf"])
