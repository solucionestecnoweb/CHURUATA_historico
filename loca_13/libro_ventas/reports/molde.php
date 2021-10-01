<odoo>
    <data>
      <record id="paperformat_libro_ventas" model="report.paperformat">

       <field name="default" eval="True"/>
        <field name="name">A4 Landscape Account</field>
        <field name="default" eval="True"/>
        <field name="format">custom</field>
        <field name="page_height">497</field>
        <field name="page_width">600</field>
        <field name="orientation">Portrait</field>
        <field name="margin_top">12</field>
        <field name="margin_bottom">15</field>
        <field name="margin_left">5</field>
        <field name="margin_right">5</field>
        <field name="header_line" eval="False"/>
        <field name="header_spacing">9</field>
        <field name="dpi">110</field>
      </record>

        <report
          id="libro_factura_clientes"
          model="account.wizard.libro.ventas"
          string="Libro de ventas"
          report_type="qweb-pdf"
          name="libro_ventas.reporte_factura_clientes"
          paperformat="libro_ventas.paperformat_libro_ventas"
          />
          <!--paperformat="libro_ventas.paperformat_libro_ventas"-->


          <template id="reporte_factura_clientes" name="">
             <t t-call="web.html_container">

                  <t t-call="web.basic_layout">
                    <t t-foreach="docs" t-as="o">
                      <div class="page">

                        <table class="table table-condensed ">
                          <tr>
                            <td colspan="26">
                              <h1>Libro de Ventas</h1>
                            </td>
                          </tr>
                          <tr>
                            <td colspan="26"><h9>Razón Social: <t t-esc="o.company_id.name"/> </h9></td>
                          </tr>
                          <tr>
                            <td colspan="26">Rif: <h9><span t-esc="o.doc_cedula2(o.company_id.id)">
                            </span></h9></td>
                          </tr>
                          <tr>
                            <td colspan="26"><h9>Dirección Fiscal:
                              <span t-field="o.company_id.street"> </span> <t t-esc="o.company_id.city" /> <t t-esc="o.company_id.state_id.name"/> <t t-esc="o.company_id.zip" /> <t t-esc="o.company_id.country_id.name" /></h9>
                            </td>
                          </tr>
                          <tr>
                            <td colspan="26"><h9>Periodo:
                              <span t-field="o.date_from"></span> &amp;nbsp;Hasta:<span t-field="o.date_to"></span></h9>
                            </td>
                          </tr>
                          <tr>
                            <td colspan="15"> </td>
                            <td colspan="8">
                              <div align="center">
                              VENTAS INTERNAS
                              </div>
                            </td>
                            <td colspan="3"></td>
                          </tr>

                          <tbody class="table table-bordered">
                          <tr>
                            <td colspan="15"> </td>
                            <td colspan="4" style="background-color:#CCCCCC">
                                <div align="center">
                                  CONTRIBUYENTES
                                </div>
                            </td>
                            <td colspan="4" style="background-color:#CCCCCC">
                                <div align="center">
                                  NO CONTRIBUYENTES
                                </div>
                            </td>
                            <td></td>
                            <td></td>
                            <td></td>
                            <!--td></td-->
                          </tr>
                          </tbody>

                          <tr>
                            <td>#</td>
                            <td>Fecha de Documento </td>
                            <td>Rif</td>
                            <td>Nombre Razón Social </td>
                            <td>Tipo de Persona </td>
                            <td>Número de Planilla<br/>
                            de Exportación</td>
                            <td>Nro Factura<br/>
                            / Entrega</td>
                            <td>Nro. de
                            Control</td>
                            <td>Número <br/>nota
                            de debito</td>
                            <td>Número <br/>
                               nota de Crédito
                          </td>
                            <td>Nro. Factura Afectada
                          </td>
                            <td>Tipo de <br/>Transacc.</td>
                            <td>Total Venta <br/> Incluyendo Iva</td>
                            <td>Valor FOB </td>
                            <td>Ventas Exentas <br/>o Exoneradas </td>                            
                            <td>Base imponible</td>
                            <td>Alicuota Reducida <br/>(8%)</td>
                            <td>Alicuota General<br/>(16%)</td>
                            <td>Impuesto Iva </td>

                            <td>Base imponible</td>
                            <td>Alicuota Reducida <br/>(8%)</td>
                            <td>Alicuota General <br/>(16%)</td>
                            <td>Impuesto Iva </td>

                            <td>IVA Retenido <br/>(Comprador)</td>
                            <td>Nro <br/>Comprobante</td>
                            <td>Fecha Comp.</td>
                            <!--td></td-->
                          </tr>
                          <!-- INICIO VARIABLES DE ENTORNOS -->
                          <t t-set="contador" t-value="0"/>
                          <t t-set="acum_venta_iva" t-value="0"/>
                          <t t-set="acum_exento" t-value="0"/>

                          <t t-set="acum_base" t-value="0"/>
                          <t t-set="acum_reducida" t-value="0"/>
                          <t t-set="acum_general" t-value="0"/>
                          <t t-set="acum_iva" t-value="0"/>

                          <t t-set="acum_adicional" t-value="0"/>

                          <t t-set="acum_base2" t-value="0"/>
                          <t t-set="acum_reducida2" t-value="0"/>
                          <t t-set="acum_general2" t-value="0"/>
                          <t t-set="acum_iva2" t-value="0"/>

                          <t t-set="acum_iva_ret" t-value="0"/>

                          <t t-set="acum_base_general" t-value="0"/>
                          <t t-set="acum_base_adicional" t-value="0"/>
                          <t t-set="acum_base_reducida" t-value="0"/>

                          <t t-set="acum_ret_general" t-value="0"/>
                          <t t-set="acum_ret_adicional" t-value="0"/>
                          <t t-set="acum_ret_reducida" t-value="0"/>

                          <t t-set="total_bases" t-value="0"/>
                          <t t-set="total_debitos" t-value="0"/>
                          <t t-set="total_retenidos" t-value="0"/>

                          <!-- FIN VARIABLES DE ENTORNOS -->

                          <tbody class="table table-bordered">
                          <t t-foreach="o.line.sorted(key=lambda x: (x.name,x.invoice_ctrl_number ),reverse=False)" t-as="line" >
                            <!-- variables para los resumenes de totales-->
                            <t t-set="contador" t-value="contador+1"/>

                            <t t-set="acum_base_general" t-value="acum_base_general+line.base_general"/>
                            <t t-set="acum_base_adicional" t-value="acum_base_adicional+line.base_adicional"/>
                            <t t-set="acum_base_reducida" t-value="acum_base_reducida+line.base_reducida"/>
                            <t t-set="acum_adicional" t-value="acum_adicional+line.alicuota_adicional"/>

                            <t t-if="line.state_retantion == 'posted' ">
                              <t t-set="acum_ret_general" t-value="acum_ret_general+line.retenido_general"/>

                              <t t-set="acum_ret_adicional" t-value="acum_ret_adicional+line.retenido_adicional"/>

                              <t t-set="acum_ret_reducida" t-value="acum_ret_reducida+line.retenido_reducida"/>
                            </t>

                            <!-- Fin variables para los resumenes de totales-->
                            <tr>
                              <td><t t-esc="contador"/></td>
                              <td><t t-esc="line.formato_fecha2(line.name)"/></td>
                              <td><t t-esc="line.doc_cedula(line.partner.id)"/></td>
                              <td><t t-esc="line.partner.name"/></td>
                              
                                <t t-if="line.partner.people_type == 'resident_nat_people' ">
                                  <td>PNRE</td>
                                </t>
                                <t t-elif="line.partner.people_type == 'non_resit_nat_people'">
                                 <td>PNNR</td>
                                </t>
                                <t t-elif="line.partner.people_type == 'domi_ledal_entity'">
                                 <td>PJDO</td>
                                </t>
                                <t t-elif="line.partner.people_type == 'legal_ent_not_domicilied'">
                                 <td>PJND</td>
                                </t>

                              <td>-</td>
                              
                              <t t-if="line.tipo_doc == '01' ">
                                  <td>
                                    <t t-esc="line.invoice_number"/>
                                  </td>
                              </t>
                              <t t-else="">
                                  <td></td>
                              </t>

                              <td><t t-esc="line.invoice_ctrl_number"/></td>
                              
                                <t t-if="line.tipo_doc == '02' ">
                                  <td><t t-esc="line.invoice_number"/></td>
                                </t>
                                <t t-else="">
                                  <td></td>
                                </t>

                              <t t-if="line.tipo_doc == '03' ">
                                  <td><t t-esc="line.invoice_number"/></td>
                                </t>
                                <t t-else="">
                                  <td></td>
                                </t>

                              <t t-if="line.tipo_doc == '02' or  line.tipo_doc == '03' ">
                                  <td><t t-esc="line.ref"/></td>
                                </t>
                                <t t-else="">
                                  <td></td>
                              </t>

                              <td><t t-esc="line.tipo_doc"/>-Reg</td>
                              <td>
                                <div align="right">
                                  <t t-esc="line.float_format(line.sale_total)"/>
                                  <t t-set="acum_venta_iva" t-value="acum_venta_iva+line.sale_total"/>
                                </div>
                              </td>
                                <!-- Total con iva-->

                              <td>
                                <div align="right">
                                ??
                                </div>
                              </td><!-- total no gravadas-->

                              <td>
                                <div align="right">
                                  <t t-esc="line.float_format(line.total_exento)"/>
                                  <t t-set="acum_exento" t-value="acum_exento+line.total_exento"/>
                                </div>
                              </td><!-- total exento-->
                              
                              <!-- CAMPOS DE CONTRIBUYENTES -->
                              <t t-if="line.partner.contribuyente == 'True'">
                                <td>
                                  <div align="right">
                                  <t t-esc="line.float_format(line.base_imponible-line.total_exento)"/>
                                  <t t-set="acum_base" t-value="acum_base+(line.base_imponible-line.total_exento)"/>
                                  </div>
                                </td>
                                <td>
                                  <div align="right">
                                  <t t-esc="line.float_format(line.alicuota_reducida)"/>
                                  <t t-set="acum_reducida" t-value="acum_reducida+line.alicuota_reducida"/>
                                  </div>
                                </td>
                                <td>
                                  <div align="right">
                                    <t t-esc="line.float_format(line.alicuota_general)"/>
                                    <t t-set="acum_general" t-value="acum_general+line.alicuota_general"/>
                                  </div>
                                </td>
                                <td>
                                  <div align="right">
                                    <t t-esc="line.float_format(line.iva)"/>
                                    <t t-set="acum_iva" t-value="acum_iva+line.iva"/>
                                  </div>
                                </td>
                              </t>

                              <t t-else="">
                                <td></td>
                                <td></td>
                                <td></td>
                                <td></td>
                              </t>

                               <!-- CAMPOS DE NO CONTRIBUYENTES -->
                              <t t-if="line.partner.contribuyente == 'False'">
                                <td>
                                  <div align="right">
                                  <t t-esc="line.float_format(line.base_imponible-line.total_exento)"/>
                                  <t t-set="acum_base2" t-value="acum_base2+(line.base_imponible-line.total_exento)"/>
                                </div>
                                </td>
                                <td>
                                  <div align="right">
                                  <t t-esc="line.float_format(line.alicuota_reducida)"/>
                                  <t t-set="acum_reducida2" t-value="acum_reducida2+line.alicuota_reducida"/>
                                </div>
                                </td>
                                <td>
                                  <div align="right">
                                  <t t-esc="line.float_format(line.alicuota_general)"/>
                                  <t t-set="acum_general2" t-value="acum_general2+line.alicuota_general"/>
                                </div>
                                </td>
                                <td>
                                  <div align="right">
                                  <t t-esc="line.float_format(line.iva)"/>
                                  <t t-set="acum_iva2" t-value="acum_iva2+line.iva"/>
                                </div>
                                </td>
                              </t>
                              <t t-else="">
                                <td></td>
                                <td></td>
                                <td></td>
                                <td></td>
                              </t>
                              <!-- Campo Iva retenido-->
                              <td>
                                <t t-if="line.vat_ret_id.state == 'posted' ">
                                <div align="right">
                                <t t-esc="line.float_format(line.iva_retenido)"/>
                                <t t-set="acum_iva_ret" t-value="acum_iva_ret+line.iva_retenido"/>
                                </div>
                                </t>
                              </td>
                              <!-- Campo Nro de Control-->
                              <td>
                                <t t-if="line.vat_ret_id.state == 'posted' ">
                                <t t-esc="line.retenido"/>
                                </t>
                              </td>

                              <!-- Campo Fecha Comprobante-->
                              <td>
                                <t t-if="line.vat_ret_id.state == 'posted' ">
                                <t t-esc="line.formato_fecha2(line.retenido_date)"/>
                                </t>
                              </td>
                            </tr>
                          </t>
                          </tbody>
                          <!-- darrell FILA DE TOTALES -->
                          <tr>
                            <td colspan="11"> </td>
                            <td><div align="right">TOTALES:</div></td>
                            <td><div align="right"><t t-esc="o.float_format2(acum_venta_iva)"/></div></td>

                            <td></td><!--totales no gravadas-->

                            <td>
                              <div align="right">
                                <t t-esc="o.float_format2(acum_exento)"/>
                              </div>
                            </td>
                            
                            <td>
                              <div align="right">
                              <t t-esc="o.float_format2(acum_base)"/>
                              </div>
                            </td>

                            <td>
                              <div align="right">
                              <t t-esc="o.float_format2(acum_reducida)"/>
                              </div>
                            </td>
                            <td>
                              <div align="right">
                              <t t-esc="o.float_format2(acum_general)"/>
                              </div>
                            </td>
                            <td>
                              <div align="right">
                              <t t-esc="o.float_format2(acum_iva)"/>
                              </div>
                            </td>
                            <td>
                              <div align="right">
                              <t t-esc="o.float_format2(acum_base2)"/>
                              </div>
                            </td>
                            <td>
                              <div align="right">
                              <t t-esc="o.float_format2(acum_reducida2)"/>
                              </div>
                            </td>
                            <td>
                              <div align="right">
                              <t t-esc="o.float_format2(acum_general2)"/>
                              </div>
                            </td>
                            <td>
                              <div align="right">
                              <t t-esc="o.float_format2(acum_iva2)"/>
                              </div>
                            </td>
                            <td>
                              <div align="right">
                              <t t-esc="o.float_format2(acum_iva_ret)"/>
                              </div>
                            </td>
                            <td colspan="2"> </td>
                          </tr>
                          <!-- FIN FILA TOTALES-->
                          <tr>
                            <td></td><!--1 -->
                            <td></td><!--2 -->
                            <td></td><!--3 -->
                            <td></td><!--4 -->
                            <td></td><!--5 -->
                            <td></td><!--6 -->
                            <td></td><!--7 -->
                            <td></td><!--8 -->
                            <td></td><!--9 -->
                            <td></td><!--10 -->
                            <td></td><!--11 -->
                            <td></td><!--12 -->

                            <td colspan="2">
                              <div align="center">
                              RESUMEN DE VENTAS
                              </div>
                            </td><!--13 --><!--14 -->  

                            <td></td><!--15 -->

                            <td colspan="2">
                              <div align="center">
                              Base Imponible
                              </div>
                            </td><!--16 --><!-- 17-->

                            <td colspan="2">
                              <div align="center">Débito Fiscal</div>
                            </td><!--18 --><!--19 -->

                            <td></td><!-- 20-->
                            <td></td><!--21 -->
                            <td></td><!-- 22-->

                            <td colspan="3">
                              <div align="center">Iva Retenido por Comp.</div>
                            </td>                       

                            <td></td><!--26 -->
                          </tr>

                          <tr>
                            <td></td><!--1-->
                            <td></td><!--2-->
                            <td></td><!--3-->
                            <td></td><!--4-->
                            <td></td><!--5-->                            
                            <td></td><!--6-->
                            <td></td><!--7-->
                            <td></td><!--8-->
                            <td></td><!--9-->
                            <td></td><!-- 10-->
                            <td></td><!-- 11-->

                            <td colspan="3">
                              Ventas Internas Afectadas sólo Alícuota General
                            </td><!-- 12--><!-- 13--><!-- 14--> 

                            <td></td><!-- 15-->

                            <td colspan="2">
                              <div align="right">
                              <t t-esc="o.float_format2(acum_base_general)"/>
                              <t t-set="total_bases" t-value="total_bases+acum_base_general"/>
                            </div>
                          </td><!-- 16--><!-- 17-->

                            <td></td><!-- 18-->
                            <td>
                              <div align="right">
                              <t t-esc="o.float_format2(acum_general+acum_general2)"/>
                              <t t-set="total_debitos" t-value="total_debitos+(acum_general+acum_general2)"/>
                              </div>
                            </td><!-- 19-->
                            <td></td><!-- 20-->
                            <td></td><!-- 21-->

                            <td colspan="3">
                              <div align="right">
                                <t t-esc="o.float_format2(acum_ret_general)"/>
                                <t t-set="total_retenidos" t-value="total_retenidos+acum_ret_general"/>
                              </div>
                            </td>
                            
                            <td></td><!-- 25-->                           
                            <td></td><!--26 -->
                            </tr>

                            <tr>

                            <td></td><!--1-->
                            <td></td><!--2-->
                            <td></td><!--3-->
                            <td></td><!--4-->
                            <td></td><!--5-->                            
                            <td></td><!--6-->
                            <td></td><!--7-->
                            <td></td><!--8-->
                            <td></td><!--9-->
                            <td></td><!-- 10-->
                            <td></td><!-- 11-->

                            <td colspan="3">
                              VentasInternas Afectadassólo AlícuotaGeneral + Adicional
                            </td><!-- 12--><!-- 13--><!-- 14--> 

                            <td></td><!-- 15-->

                            <td colspan="2">
                              <div align="right">
                              <t t-esc="o.float_format2(acum_base_adicional)"/>
                              <t t-set="total_bases" t-value="total_bases+acum_base_adicional"/>
                              </div>
                            </td><!-- 16--><!-- 17-->
                            <td></td><!-- 18-->
                            <td>
                              <div align="right">
                              <t t-esc="o.float_format2(acum_adicional)"/>
                              <t t-set="total_debitos" t-value="total_debitos+acum_adicional"/>
                              </div>
                            </td><!-- 19-->
                            <td></td><!-- 20-->
                            <td></td><!-- 21-->

                            <td colspan="3">
                              <div align="right">
                                <t t-esc="o.float_format2(acum_ret_adicional)"/>
                                <t t-set="total_retenidos" t-value="total_retenidos+acum_ret_adicional"/>
                              </div>
                            </td>
                            
                            <td></td><!-- 25-->                           
                            <td></td><!--26 -->
                            </tr>

                            <tr>
                            <td></td><!--1-->
                            <td></td><!--2-->
                            <td></td><!--3-->
                            <td></td><!--4-->
                            <td></td><!--5-->                            
                            <td></td><!--6-->
                            <td></td><!--7-->
                            <td></td><!--8-->
                            <td></td><!--9-->
                            <td></td><!-- 10-->
                            <td></td><!-- 11-->

                            <td colspan="3">
                              VentasInternas Afectadassólo Alícuota Reducida
                            </td><!-- 12--><!-- 13--><!-- 14--> 

                            <td></td><!-- 15-->

                            <td colspan="2">
                              <div align="right">
                              <t t-esc="o.float_format2(acum_base_reducida)"/>
                              <t t-set="total_bases" t-value="total_bases+acum_base_reducida"/>
                              </div>
                            </td><!-- 16--><!-- 17-->
                            <td></td><!-- 18-->
                            <td>
                              <div align="right">
                              <t t-esc="o.float_format2(acum_reducida+acum_reducida2)"/>
                              <t t-set="total_debitos" t-value="total_debitos+(acum_reducida+acum_reducida2)"/>
                              </div>
                            </td><!-- 19-->
                            <td></td><!-- 20-->
                            <td></td><!-- 21-->

                            <td colspan="3">
                              <div align="right">
                                <t t-esc="o.float_format2(acum_ret_reducida)"/>
                                <t t-set="total_retenidos" t-value="total_retenidos+acum_ret_reducida"/>
                              </div>
                            </td>
                            
                            <td></td><!-- 25-->                           
                            <td></td><!--26 -->
                            </tr>

                            <tr>
                            <td></td><!--1-->
                            <td></td><!--2-->
                            <td></td><!--3-->
                            <td></td><!--4-->
                            <td></td><!--5-->                            
                            <td></td><!--6-->
                            <td></td><!--7-->
                            <td></td><!--8-->
                            <td></td><!--9-->
                            <td></td><!-- 10-->
                            <td></td><!-- 11-->

                            <td colspan="3">
                              Ventasinternas Exentas o Exoneradas
                            </td><!-- 12--><!-- 13--><!-- 14-->                           
                            <td></td><!-- 15-->

                            <td colspan="2">
                              <div align="right">
                                <t t-esc="o.float_format2(acum_exento)"/>
                                <t t-set="total_bases" t-value="total_bases+acum_exento"/>
                              </div>
                            </td><!-- 16--><!-- 17-->
                            <td></td><!-- 18-->
                            <td><div align="right">0,00</div></td><!-- 19-->
                            <td></td><!-- 20-->
                            <td></td><!-- 21-->

                            <td colspan="3"><div align="right">0,00</div></td>
                            <td></td><!-- 25-->                           
                            <td></td><!--26 -->
                            </tr>

                            <tr>
                            <td></td><!--1-->
                            <td></td><!--2-->
                            <td></td><!--3-->
                            <td></td><!--4-->
                            <td></td><!--5-->                            
                            <td></td><!--6-->
                            <td></td><!--7-->
                            <td></td><!--8-->
                            <td></td><!--9-->
                            <td></td><!-- 10-->
                            <td></td><!-- 11-->

                            <td colspan="3">
                              Total:
                            </td><!-- 12--><!-- 13--><!-- 14-->                           
                            <td></td><!-- 15-->

                            <td colspan="2">
                              <div align="right">
                              <t t-esc="o.float_format2(total_bases)"/>
                              </div>
                            </td><!-- 16--><!-- 17-->
                            <td></td><!-- 18-->
                            <td>
                              <div align="right">
                              <t t-esc="total_debitos"/>
                              </div>
                            </td><!-- 19-->
                            <td></td><!-- 20-->
                            <td></td><!-- 21-->

                            <td colspan="3">
                              <div align="right">
                                <t t-esc="o.float_format2(total_retenidos)"/>
                              </div>
                            </td>

                            <td></td><!-- 25-->                           
                            <td></td><!--26 -->
                            </tr>

                            <!--tr>
                            <td>17</td>
                            <td>2</td>
                            <td>3</td>
                            <td>4</td>
                            <td>5</td>
                            <td>6</td>
                            <td>7</td>
                            <td>8</td>
                            <td>9</td>
                            <td>10</td>
                            <td>11</td>
                            <td>12</td>
                            <td>13</td>
                            <td>14</td>
                            <td>15</td>
                            <td>16</td>
                            <td>17</td>
                            <td>18</td>
                            <td>19</td>
                            <td>20</td>
                            <td>21</td>
                            <td>22</td>
                            <td>23</td>
                            <td>24</td>
                            <td>25</td>
                            <td>26</td>
                            </tr-->

                            <tr>
                            <td>18</td>
                            <td>2</td>
                            <td>3</td>
                            <td>4</td>
                            <td>5</td>
                            <td>6</td>
                            <td>7</td>
                            <td>8</td>
                            <td>9</td>
                            <td>10</td>
                            <td>11</td>
                            <td>12</td>
                            <td>13</td>
                            <td>14</td>
                            <td>15</td>
                            <td>16</td>
                            <td>17</td>
                            <td>18</td>
                            <td>19</td>
                            <td>20</td>
                            <td>21</td>
                            <td>22</td>
                            <td>23</td>
                            <td>24</td>
                            <td>25</td>
                            <td>26</td>
                          </tr>
                        </table>

                      </div>

                  </t>
              </t>
            </t>
          </template>
     </data>
</odoo>
