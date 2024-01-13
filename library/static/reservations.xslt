<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

	<xsl:template match="/">
		<table id="reservations_list">
			<tr>
				<th>Book</th>
				<th>Start Date</th>
				<th>End Date</th>
				<th>Reminder</th>
				<th>Additional Info</th>
			</tr>
			<xsl:apply-templates select="reservations/reservation"/>
		</table>
	</xsl:template>
	
	<xsl:template match="reservation">
		<tr>
			<xsl:if test="is_active = 'False'">
				<xsl:attribute name="style">color: darkgrey;</xsl:attribute>
			</xsl:if>
			<td>
				<xsl:value-of select="book"/>
			</td>
			<td>
				<xsl:value-of select="start_date"/>
			</td>
			<td>
				<xsl:value-of select="end_date"/>
			</td>
			<td>
				<xsl:if test="should_remind = 'True'">
					On
				</xsl:if>
				<xsl:if test="should_remind = 'False'">
					Off
				</xsl:if>
			</td>
			<td>
				<xsl:value-of select="add_info"/>
			</td>
		</tr>
	</xsl:template>
</xsl:stylesheet>
