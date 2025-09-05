"""
Módulo para geração de PDFs de comprovantes e contratos.

Este módulo é responsável por gerar PDFs padronizados para:
- Comprovantes de despesas
- Comprovantes de receitas
- Contratos de empréstimos
- Relatórios de transferências
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional
from io import BytesIO

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from utils.date_utils import (
    format_date_for_display,
    format_currency_br
)
from config.settings import db_categories


logger = logging.getLogger(__name__)


class PDFGenerator:
    """Classe para geração de PDFs de comprovantes e contratos."""

    def __init__(self):
        """Inicializa o gerador de PDF."""
        if not REPORTLAB_AVAILABLE:
            raise ImportError(
                "ReportLab não está instalado. "
                "Execute: pip install reportlab"
            )

        self.page_size = A4
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Configura estilos customizados para os PDFs."""
        # Estilo para título
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            textColor=colors.HexColor('#2E86AB'),
            alignment=1  # Center
        ))

        # Estilo para subtítulo
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=12,
            spaceAfter=20,
            textColor=colors.HexColor('#A23B72'),
            alignment=1  # Center
        ))

        # Estilo para dados importantes
        self.styles.add(ParagraphStyle(
            name='ImportantData',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            textColor=colors.HexColor('#F18F01'),
            leftIndent=20
        ))

    def generate_expense_receipt(
        self,
        expense_data: Dict[str, Any],
        account_data: Optional[Dict[str, Any]] = None
    ) -> BytesIO:
        """
        Gera comprovante de despesa.

        Parameters
        ----------
        expense_data : Dict[str, Any]
            Dados da despesa
        account_data : Dict[str, Any], optional
            Dados da conta

        Returns
        -------
        BytesIO
            Buffer com o PDF gerado
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=self.page_size)
        story = []

        # Cabeçalho
        title = Paragraph("COMPROVANTE DE DESPESA", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 20))

        # Informações da despesa
        expense_info = [
            ["Descrição:", expense_data.get('description', 'N/A')],
            [
                "Valor:", format_currency_br(float(
                    expense_data.get('value', 0)
                ))
            ],
            ["Data:", format_date_for_display(expense_data.get('date', ''))],
            ["Horário:", expense_data.get('horary', 'N/A')],
            ["Categoria:", db_categories.EXPENSE_CATEGORIES.get(
                expense_data.get('category', 'others'),
                expense_data.get('category', 'N/A')
            )],
            ["Status:", "✅ Paga" if expense_data.get(
                'payed', False) else "⏳ Pendente"]
        ]

        if account_data:
            account_name = db_categories.INSTITUTIONS.get(
                account_data.get('name', ''),
                account_data.get('name', 'N/A')
            )
            expense_info.append(["Conta:", account_name])

        # Tabela com informações
        table = Table(expense_info, colWidths=[2 * inch, 4 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8F4FD')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#CCCCCC'))
        ]))

        story.append(table)
        story.append(Spacer(1, 30))

        # Rodapé
        footer_text = f"""
        <para align="center">
        Este comprovante foi gerado automaticamente pelo sistema ExpenseLit
        <br/>
        Data de emissão: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}<br/>
        ID da despesa: {expense_data.get('id', 'N/A')}
        </para>
        """
        footer = Paragraph(footer_text, self.styles['Normal'])
        story.append(footer)

        doc.build(story)
        buffer.seek(0)
        return buffer

    def generate_revenue_receipt(
        self,
        revenue_data: Dict[str, Any],
        account_data: Optional[Dict[str, Any]] = None
    ) -> BytesIO:
        """
        Gera comprovante de receita.

        Parameters
        ----------
        revenue_data : Dict[str, Any]
            Dados da receita
        account_data : Dict[str, Any], optional
            Dados da conta

        Returns
        -------
        BytesIO
            Buffer com o PDF gerado
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=self.page_size)
        story = []

        # Cabeçalho
        title = Paragraph("COMPROVANTE DE RECEITA", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 20))

        # Informações da receita
        revenue_info = [
            ["Descrição:", revenue_data.get('description', 'N/A')],
            [
                "Valor:", format_currency_br(float(
                    revenue_data.get('value', 0))
                )
            ],
            ["Data:", format_date_for_display(revenue_data.get('date', ''))],
            ["Horário:", revenue_data.get('horary', 'N/A')],
            ["Categoria:", db_categories.REVENUE_CATEGORIES.get(
                revenue_data.get('category', 'others'),
                revenue_data.get('category', 'N/A')
            )],
            ["Status:", "✅ Recebida" if revenue_data.get(
                'received', False) else "⏳ Pendente"]
        ]

        if account_data:
            account_name = db_categories.INSTITUTIONS.get(
                account_data.get('name', ''),
                account_data.get('name', 'N/A')
            )
            revenue_info.append(["Conta:", account_name])

        # Tabela com informações
        table = Table(revenue_info, colWidths=[2 * inch, 4 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8FDF0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#CCCCCC'))
        ]))

        story.append(table)
        story.append(Spacer(1, 30))

        # Rodapé
        footer_text = f"""
        <para align="center">
        Este comprovante foi gerado automaticamente pelo sistema ExpenseLit
        <br/>
        Data de emissão: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}<br/>
        ID da receita: {revenue_data.get('id', 'N/A')}
        </para>
        """
        footer = Paragraph(footer_text, self.styles['Normal'])
        story.append(footer)

        doc.build(story)
        buffer.seek(0)
        return buffer

    def generate_loan_contract(
        self,
        loan_data: Dict[str, Any],
        creditor_data: Optional[Dict[str, Any]] = None,
        benefited_data: Optional[Dict[str, Any]] = None
    ) -> BytesIO:
        """
        Gera contrato de empréstimo.

        Parameters
        ----------
        loan_data : Dict[str, Any]
            Dados do empréstimo
        creditor_data : Dict[str, Any], optional
            Dados do credor
        benefited_data : Dict[str, Any], optional
            Dados do beneficiado

        Returns
        -------
        BytesIO
            Buffer com o PDF gerado
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=self.page_size)
        story = []

        # Cabeçalho
        title = Paragraph("CONTRATO DE EMPRÉSTIMO", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 20))

        # Partes do contrato
        parties_text = f"""
        <para align="justify">
        <b>CREDOR:</b> {loan_data.get('creditor_name', 'N/A')}<br/>
        <b>DEVEDOR:</b> {loan_data.get('benefited_name', 'N/A')}<br/>
        </para>
        """
        parties = Paragraph(parties_text, self.styles['Normal'])
        story.append(parties)
        story.append(Spacer(1, 20))

        # Informações do empréstimo
        loan_info = [
            ["Descrição:", loan_data.get('description', 'N/A')],
            ["Valor Total:", format_currency_br(
                float(loan_data.get('value', 0)))],
            ["Valor Pago:", format_currency_br(
                float(loan_data.get('payed_value', 0)))],
            ["Saldo Devedor:", format_currency_br(
                float(loan_data.get('value', 0)) - float(
                    loan_data.get('payed_value', 0)
                )
            )],
            ["Data do Empréstimo:", format_date_for_display(
                loan_data.get('date', ''))],
            ["Horário:", loan_data.get('horary', 'N/A')],
            ["Categoria:", db_categories.EXPENSE_CATEGORIES.get(
                loan_data.get('category', 'others'),
                loan_data.get('category', 'N/A')
            )],
            ["Status:", "✅ Quitado" if loan_data.get(
                'payed', False) else "⏳ Em Aberto"]
        ]

        # Tabela com informações
        table = Table(loan_info, colWidths=[2.5 * inch, 3.5 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#FDF4E8')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#CCCCCC'))
        ]))

        story.append(table)
        story.append(Spacer(1, 30))

        # Cláusulas do contrato
        clauses_text = f"""
        <para align="justify">
        <b>CLÁUSULAS:</b><br/><br/>

        <b>1.</b> O presente contrato refere-se ao empréstimo no valor de
        <b>{format_currency_br(float(loan_data.get('value', 0)))}</b>,
realizado em <b>{format_date_for_display(loan_data.get('date', ''))}</b>.
            <br/>
        <br/>

<b>2.</b> O devedor compromete-se a quitar o valor em \
    prestado conforme acordado entre as partes.<br/><br/>

<b>3.</b> Este contrato é meramente informativo e foi g \
    erado automaticamente pelo sistema ExpenseLit.<br/><br/>

<b>4.</b> Para questões legais, consulte u \
    m advogado especializado em contratos.<br/>
        </para>
        """
        clauses = Paragraph(clauses_text, self.styles['Normal'])
        story.append(clauses)
        story.append(Spacer(1, 30))

        # Rodapé
        footer_text = f"""
        <para align="center">
        Este contrato foi gerado automaticamente pelo sistema ExpenseLit<br/>
        Data de emissão: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}<br/>
        ID do empréstimo: {loan_data.get('id', 'N/A')}
        </para>
        """
        footer = Paragraph(footer_text, self.styles['Normal'])
        story.append(footer)

        doc.build(story)
        buffer.seek(0)
        return buffer

    def generate_transfer_receipt(
        self,
        transfer_data: Dict[str, Any],
        origin_account: Optional[Dict[str, Any]] = None,
        destination_account: Optional[Dict[str, Any]] = None
    ) -> BytesIO:
        """
        Gera comprovante de transferência.

        Parameters
        ----------
        transfer_data : Dict[str, Any]
            Dados da transferência
        origin_account : Dict[str, Any], optional
            Dados da conta de origem
        destination_account : Dict[str, Any], optional
            Dados da conta de destino

        Returns
        -------
        BytesIO
            Buffer com o PDF gerado
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=self.page_size)
        story = []

        # Cabeçalho
        title = Paragraph(
            "COMPROVANTE DE TRANSFERÊNCIA", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 20))

        # Informações da transferência
        transfer_info = [
            ["Descrição:", transfer_data.get('description', 'N/A')],
            ["Valor:", format_currency_br(
                float(transfer_data.get('value', 0)))],
            ["Data:", format_date_for_display(transfer_data.get('date', ''))],
            ["Horário:", transfer_data.get('horary', 'N/A')],
        ]

        if origin_account:
            origin_name = db_categories.INSTITUTIONS.get(
                origin_account.get('name', ''),
                origin_account.get('name', 'N/A')
            )
            transfer_info.append(["Conta Origem:", origin_name])

        if destination_account:
            dest_name = db_categories.INSTITUTIONS.get(
                destination_account.get('name', ''),
                destination_account.get('name', 'N/A')
            )
            transfer_info.append(["Conta Destino:", dest_name])

        # Tabela com informações
        table = Table(transfer_info, colWidths=[2 * inch, 4 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F0E8FD')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#CCCCCC'))
        ]))

        story.append(table)
        story.append(Spacer(1, 30))

        # Rodapé
        footer_text = f"""
        <para align="center">
        Este comprovante foi gerado automaticamente pelo sistema ExpenseLit
        <br/>
        Data de emissão: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}<br/>
        ID da transferência: {transfer_data.get('id', 'N/A')}
        </para>
        """
        footer = Paragraph(footer_text, self.styles['Normal'])
        story.append(footer)

        doc.build(story)
        buffer.seek(0)
        return buffer

    def generate_credit_card_receipt(
        self,
        expense_data: Dict[str, Any],
        card_data: Optional[Dict[str, Any]] = None,
        bill_data: Optional[Dict[str, Any]] = None
    ) -> BytesIO:
        """
        Gera comprovante de despesa de cartão de crédito.

        Parameters
        ----------
        expense_data : Dict[str, Any]
            Dados da despesa
        card_data : Dict[str, Any], optional
            Dados do cartão
        bill_data : Dict[str, Any], optional
            Dados da fatura

        Returns
        -------
        BytesIO
            Buffer com o PDF gerado
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=self.page_size)
        story = []

        # Cabeçalho
        title = Paragraph(
            "COMPROVANTE DE DESPESA - CARTÃO DE CRÉDITO",
            self.styles['CustomTitle']
        )
        story.append(title)
        story.append(Spacer(1, 20))

        # Informações da despesa
        expense_info = [
            ["Descrição:", expense_data.get('description', 'N/A')],
            ["Valor:", format_currency_br(float(
                expense_data.get('value', 0)))],
            ["Data:", format_date_for_display(expense_data.get('date', ''))],
            ["Horário:", expense_data.get('horary', 'N/A')],
            ["Categoria:", db_categories.EXPENSE_CATEGORIES.get(
                expense_data.get('category', 'others'),
                expense_data.get('category', 'N/A')
            )],
            ["Cartão:", expense_data.get('card_name', 'N/A')],
        ]

        # Informações de parcelamento
        installment = expense_data.get('installment', 1)
        total_installments = expense_data.get('total_installments', 1)

        if total_installments > 1:
            expense_info.append([
                "Parcelamento:",
                f"{installment}/{total_installments}x"
            ])
        else:
            expense_info.append(["Parcelamento:", "À vista"])

        expense_info.append([
            "Status:",
            "✅ Paga" if expense_data.get('payed', False) else "⏳ Pendente"
        ])

        # Informações opcionais
        if expense_data.get('merchant'):
            expense_info.append(
                ["Estabelecimento:", expense_data.get('merchant')])

        if expense_data.get('location'):
            expense_info.append(["Local:", expense_data.get('location')])

        if expense_data.get('transaction_id'):
            expense_info.append(
                ["ID Transação:", expense_data.get('transaction_id')])

        # Tabela com informações
        table = Table(expense_info, colWidths=[2 * inch, 4 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#FDE8E8')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#CCCCCC'))
        ]))

        story.append(table)
        story.append(Spacer(1, 30))

        # Informações da fatura se disponível
        if bill_data:
            bill_text = f"""
            <para align="center">
            <b>INFORMAÇÕES DA FATURA</b><br/>
Fatura: {bill_data.get('month', 'N/A')}/{bill_data.get('year', 'N/A')}<br/>
Vencimento: {format_date_for_display(bill_data.get('due_date', ''))}<br/>
Status: {'Fechada' if bill_data.get('closed', False) else 'Em aberto'}
            </para>
            """
            bill_info = Paragraph(bill_text, self.styles['Normal'])
            story.append(bill_info)
            story.append(Spacer(1, 20))

        # Rodapé
        footer_text = f"""
        <para align="center">
        Este comprovante foi gerado automaticamente pelo sistema ExpenseLit
        <br/>
        Data de emissão: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}<br/>
        ID da despesa: {expense_data.get('id', 'N/A')}
        </para>
        """
        footer = Paragraph(footer_text, self.styles['Normal'])
        story.append(footer)

        doc.build(story)
        buffer.seek(0)
        return buffer


# Instância global do gerador
pdf_generator: Optional[PDFGenerator]
try:
    pdf_generator = PDFGenerator()
except ImportError:
    pdf_generator = None
    logger.warning(
        """
        PDFGenerator não pôde ser inicializado. ReportLab não está disponível.
        """
    )
