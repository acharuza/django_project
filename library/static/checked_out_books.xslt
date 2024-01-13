<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <xsl:template match="/">
		<table id="checked_out_list">
			<tr>
				<th>Book</th>
				<th>Start Date</th>
				<th>Due Date</th>
				<th>End Date</th>
				<th>Penalty</th>
			</tr>
			<xsl:apply-templates select="checked_out_books/checked_out_book">
				<xsl:sort select="start_date" order="ascending"/>
			</xsl:apply-templates>
		</table>
	</xsl:template>

    <xsl:template match="checked_out_book">
		<tr>
			<xsl:if test="penalty &lt; 0">
				<xsl:if test="is_penalty_paid = 'False'">
					<xsl:attribute name="style">color: #8B0000;</xsl:attribute>
				</xsl:if>
			</xsl:if>
			<td>
				<xsl:value-of select="book"/>
			</td>
			<td>
				<xsl:value-of select="start_date"/>
			</td>
			<td>
				<xsl:value-of select="due_date"/>
			</td>
			<td>
				<xsl:value-of select="end_date"/>
			</td>
			<td>
				<xsl:value-of select="format-number(penalty, '#.00')"/>
			</td>
		</tr>
	</xsl:template>

</xsl:stylesheet>