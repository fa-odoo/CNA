# -*- coding: utf-8 -*-

from PyPDF2 import utils
from odoo.exceptions import UserError
from odoo import api, fields, models, _
import base64
import io


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def _post_pdf(self, save_in_attachment, pdf_content=None, res_ids=None):
        result = super(IrActionsReport, self)._post_pdf(save_in_attachment, pdf_content, res_ids)

        if self.model == 'cna.incident':
            def close_streams(streams):
                for stream in streams:
                    try:
                        stream.close()
                    except Exception:
                        pass
            # Transform the bytes to streams
            streams = [io.BytesIO(result)]
            # Get the cna.incident records ids
            cna_record_ids = self.env[self.model].browse([res_id for res_id in res_ids if res_id])
            for cna_record_id in cna_record_ids:
                if cna_record_id.report_file:
                    # Decode PDF files to bytes
                    report_file_decode = base64.b64decode(cna_record_id.report_file)
                    # Convert to stream
                    pdf_content_stream = io.BytesIO(report_file_decode)
                    streams.append(pdf_content_stream)

            if len(streams) == 1:
                result = streams[0].getvalue()
            else:
                try:
                    result = self._merge_pdfs(streams)
                except utils.PdfReadError:
                    raise UserError(_("L'un des documents que vous essayez de fusionner est crypté"))

            close_streams(streams)
        return result