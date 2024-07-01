# Diplomski rad / Master's thesis

Usporedba brzine prijenosa **Protobuf** i **JSON** poruka u **Apache Kafka** sustavu

Comparison of transmission speed of **Protobuf** and **JSON** messages in an **Apache Kafka** system




## Docs

- [Protobuf implementation repo](https://github.com/confluentinc/confluent-kafka-python/blob/master/examples/protobuf_producer.py)
- [Protobuf docs](https://protobuf.dev)
- [shtef21/diplomski](https://github.com/shtef21/diplomski)
- [Resulting measurements](https://github.com/shtef21/diplomski/tree/main/output/graphs/dump_2024-06-18)




## Motivation

**Questions (2023-11-10):**
- How to improve communication in a Kafka producer-consumer communication?
- Is it possible to use a better method than JSON? Protocol Buffers?

**Protocol Buffers:**
- Contain object structure
- Used to create Kafka producer and consumer that utilize Protocol Buffers
- Use Schema Registry as a place to store all object definitions

**Purpose:**
- Achieve a sort of Swagger for Kafka messaging
- Optimize communication speed

**Example project structure:**
1. Repo which produces data
2. Repo which consumes data
3. Repo which contains Protobuf schemas

**Schema registry benefit**
- As soon as Kafka message structure
is changed, all consumers may be notified with a message such as
'Kafka message on topic TOPIC_NAME is updated'.




## How to run it?

### Setup Python & Docker

```sh
# Setup Python
pip install confluent-kafka protobuf requests colorama tqdm matplotlib pandas

# Startup Apache Kafka
docker compose up
```



### Initialize producer and consumer

If topics aren't initialized properly, then both JSON and PROTO consumers
will throw error. For that reason, a dry run must be executed to initialize topics.

```sh
# Run producers to create topics properly
# This script may be exited with ^C as soon
#   at least one message is produced on topics:
#   diplomski_info, diplomski_json and
#   diplomski_proto
python main.py --run-producers

# In a separate CLI, run following commands one by one
# Those commands are responsible for consuming messages
#   which were used during system initialization,
#   but shouldn't be used when calculating stats
python main.py --json-consumer --dry-run
python main.py --proto-consumer --dry-run

```



### Run measurements

To do proper measurements, first the consumers must be started.
If producers were to be started first, then there would be
delays in measurements which would make them incorrect.

Run consumers in **two CLIs simultaneously**:
```sh
# Run JSON consumer
python main.py --json-consumer

# Run PROTO consumer
python main.py --proto-consumer
```

After they initialize properly, start producers and follow the instructions:
```sh
python main.py --run-producers
```

After producers are done exited automatically, and all their messages
are consumed, both consumers must be stopped with ^C. This will
initiate processing of measurements which will be saved to **/sql.db** file.

Afterwards, it is recommended to save the sqlite3 DB file to **/sql_dumps**
directory, which will be used later in data processing. An example would be
saving it to a file on path **/sql_dumps/dump_2024-06-18.db**.



### Process measurements

Measurements are processed further to group data and calculate
things like **AVG** and **SUM** values, and **VAR** and **STD**.

The following command processes DB measurements and outputs
a CSV file on path **/output/csv/dump_2024-06-18.csv**:
```sh
python main.py --process-stats db-path ./sql_dumps/dump_2024-06-18.db
```

Generated CSV file may be opened with MS Excel, which provides
additional statistical analysis.



### Generate output graphs using processed measurements

To generate graphs using generated CSV files, following command is used:
```sh
python main.py --show-stats --csv-path ./output/csv/dump_2024-06-18.csv
```

After the command, following *matplotlib* graphs are created inside
the newly created directory **/output/dump_2024-06-18**:
- 1-serialize_duration.png
- 2-produce_duration.png
- 3-consume_duration.png
- 4-consumed_size_kb.png
- 5-deserialize_duration.png
- 6-total_serialization_duration.png
- 7-throughput_mbps.png



### Thesis PDF with system documentation and result analysis

- WIP


### Results based on 2024-06-18 measurements

<table style='border: 1px solid #888888'>
  <thead>
    <th>user_count</th>
    <th>type</th>
    <th>serialize_duration_mean</th>
    <th>serialize_duration_sum</th>
    <th>serialize_duration_var</th>
    <th>serialize_duration_std</th>
    <th>produce_duration_mean</th>
    <th>produce_duration_sum</th>
    <th>produce_duration_var</th>
    <th>produce_duration_std</th>
    <th>consume_duration_mean</th>
    <th>consume_duration_sum</th>
    <th>consume_duration_var</th>
    <th>consume_duration_std</th>
    <th>consumed_size_kb_mean</th>
    <th>consumed_size_kb_sum</th>
    <th>consumed_size_kb_var</th>
    <th>consumed_size_kb_std</th>
    <th>deserialize_duration_mean</th>
    <th>deserialize_duration_sum</th>
    <th>deserialize_duration_var</th>
    <th>deserialize_duration_std</th>
    <th>total_serialization_duration_mean</th>
    <th>total_serialization_duration_sum</th>
    <th>total_serialization_duration_var</th>
    <th>total_serialization_duration_std</th>
    <th>throughput_mbps_mean</th>
    <th>throughput_mbps_sum</th>
    <th>throughput_mbps_var</th>
    <th>throughput_mbps_std</th>
    <td>instance_count</td>
  </thead>
  <tr>
    <td>1</td>
    <td><strong>json</strong></td>
    <td>0.0283</td><td>5.6626</td><td>0.0268</td><td>0.1637</td><td>10.4796</td><td>2095.9384</td><td>4282.6635</td><td>65.4420</td><td>11.6206</td><td>2324.1388</td><td>4273.7954</td><td>65.3742</td><td>0.1565</td><td>31.3046</td><td>3.0207-06</td><td>0.0017</td><td>0.0696</td><td>13.9224</td><td>0.0260</td><td>0.1614</td><td>0.0979</td><td>19.5851</td><td>0.0586</td><td>0.2421</td><td>0.0226</td><td>4.5338</td><td>1.4953-05</td><td>0.0038</td><td>200</td>
  </tr>
  <tr bgcolor='#f6f6f6'>
    <td>1</td>
    <td><strong>proto</strong></td>
    <td>0.2873</td><td>57.4736</td><td>12.6690</td><td>3.5593</td><td>10.5976</td><td>2119.5318</td><td>4846.5375</td><td>69.6170</td><td>11.5743</td><td>2314.8691</td><td>4847.6537</td><td>69.6250</td><td>0.0858</td><td>17.1757</td><td>6.3642-08</td><td>0.0002</td><td>0.1516</td><td>30.3359</td><td>0.0602</td><td>0.2455</td><td>0.4390</td><td>87.8095</td><td>12.6483</td><td>3.5564</td><td>0.0129</td><td>2.5887</td><td>5.1085-06</td><td>0.0022</td><td>200</td>
  </tr>
  <tr>
    <td>50</td>
    <td><strong>json</strong></td>
    <td>0.1376</td><td>27.5218</td><td>0.1662</td><td>0.4077</td><td>6.6143</td><td>1322.8700</td><td>7.3327</td><td>2.7079</td><td>8.0637</td><td>1612.7426</td><td>8.6170</td><td>2.9354</td><td>8.0437</td><td>1608.7597</td><td>0.0020</td><td>0.0455</td><td>0.3690</td><td>73.8146</td><td>0.1083</td><td>0.3292</td><td>0.5066</td><td>101.3364</td><td>0.2658</td><td>0.5156</td><td>1.0320</td><td>206.4134</td><td>0.0384</td><td>0.1961</td><td>200</td>
  </tr>
  <tr bgcolor='#f6f6f6'>
    <td>50</td>
    <td><strong>proto</strong></td>
    <td>0.1227</td><td>24.5597</td><td>0.1426</td><td>0.3777</td><td>6.6743</td><td>1334.8603</td><td>23.6012</td><td>4.8581</td><td>7.9267</td><td>1585.3440</td><td>24.0989</td><td>4.9090</td><td>3.9581</td><td>791.6240</td><td>3.4905-06</td><td>0.0018</td><td>0.1265</td><td>25.3007</td><td>0.0460</td><td>0.2146</td><td>0.2493</td><td>49.8604</td><td>0.1979</td><td>0.4449</td><td>0.5319</td><td>106.3852</td><td>0.0149</td><td>0.1221</td><td>200</td>
  </tr>
  <tr>
    <td>100</td>
    <td><strong>json</strong></td>
    <td>0.7180</td><td>143.6030</td><td>58.1445</td><td>7.6252</td><td>7.2066</td><td>1441.3399</td><td>6.5663</td><td>2.5624</td><td>8.9043</td><td>1780.8797</td><td>7.6225</td><td>2.7608</td><td>16.3983</td><td>3279.6689</td><td>7.6255-06</td><td>0.0027</td><td>0.7143</td><td>142.8663</td><td>0.1252</td><td>0.3539</td><td>1.4323</td><td>286.4694</td><td>58.2676</td><td>7.6333</td><td>1.8822</td><td>376.4510</td><td>0.1069</td><td>0.3270</td><td>200</td>
  </tr>
  <tr bgcolor='#f6f6f6'>
    <td>100</td>
    <td><strong>proto</strong></td>
    <td>0.1853</td><td>37.0798</td><td>0.3039</td><td>0.5513</td><td>6.8960</td><td>1379.2033</td><td>2.5845</td><td>1.6076</td><td>8.3640</td><td>1672.8067</td><td>4.6365</td><td>2.1532</td><td>7.9093</td><td>1581.8662</td><td>9.0967-06</td><td>0.0030</td><td>0.1437</td><td>28.7415</td><td>0.0537</td><td>0.2319</td><td>0.3291</td><td>65.8214</td><td>0.3478</td><td>0.5897</td><td>0.9612</td><td>192.2541</td><td>0.0278</td><td>0.1667</td><td>200</td>
  </tr>
  <tr>
    <td>500</td>
    <td><strong>json</strong></td>
    <td>0.5655</td><td>113.1160</td><td>1.8230</td><td>1.3502</td><td>18.5797</td><td>3715.9550</td><td>5117.4593</td><td>71.5364</td><td>24.3619</td><td>4872.3824</td><td>5145.7109</td><td>71.7336</td><td>81.8292</td><td>16365.8554</td><td>0.2519</td><td>0.5019</td><td>3.0748</td><td>614.9723</td><td>0.5209</td><td>0.7217</td><td>3.6404</td><td>728.0883</td><td>2.2594</td><td>1.5031</td><td>4.4294</td><td>885.8801</td><td>0.8318</td><td>0.9120</td><td>200</td>
  </tr>
  <tr bgcolor='#f6f6f6'>
    <td>500</td>
    <td><strong>proto</strong>
    </td><td>1.2095</td><td>241.9185</td><td>12.1249</td><td>3.4820</td><td>15.3850</td><td>3077.0177</td><td>3987.2103</td><td>63.1443</td><td>17.8478</td><td>3569.5683</td><td>3993.0739</td><td>63.1907</td><td>39.3292</td><td>7865.8505</td><td>0.2345</td><td>0.4843</td><td>0.5970</td><td>119.4007</td><td>0.2271</td><td>0.4765</td><td>1.8065</td><td>361.3193</td><td>12.0032</td><td>3.4645</td><td>3.0826</td><td>616.5382</td><td>0.5771</td><td>0.7597</td><td>200</td>
  </tr>
  <tr>
    <td>1000</td>
    <td><strong>json</strong></td>
    <td>1.3296</td><td>265.9235</td><td>5.3932</td><td>2.3223</td><td>23.5407</td><td>4708.1437</td><td>91.9854</td><td>9.5909</td><td>36.1392</td><td>7227.8597</td><td>151.3475</td><td>12.3023</td><td>163.6585</td><td>32731.7109</td><td>0.9085</td><td>0.9531</td><td>5.9658</td><td>1193.1684</td><td>56.8340</td><td>7.5388</td><td>7.2954</td><td>1459.0919</td><td>64.2766</td><td>8.0172</td><td>4.7674</td><td>953.4895</td><td>1.1794</td><td>1.0860</td><td>200</td>
  </tr>
  <tr bgcolor='#f6f6f6'>
    <td>1000</td>
    <td><strong>proto</strong></td>
    <td>1.2598</td><td>251.9764</td><td>5.9163</td><td>2.4323</td><td>17.5086</td><td>3501.7387</td><td>35.5394</td><td>5.9614</td><td>25.4798</td><td>5095.9758</td><td>98.9684</td><td>9.9482</td><td>78.6516</td><td>15730.3339</td><td>0.8730</td><td>0.9343</td><td>1.2788</td><td>255.7673</td><td>1.0494</td><td>1.0244</td><td>2.5387</td><td>507.7438</td><td>6.7463</td><td>2.5973</td><td>3.3265</td><td>665.3087</td><td>0.8945</td><td>0.9457</td><td>200</td></tr>
  <tr>
    <td>2500</td>
    <td><strong>json</strong></td>
    <td>2.0416</td><td>408.3392</td><td>16.4638</td><td>4.0575</td><td>66.3222</td><td>13264.4543</td><td>4835.6211</td><td>69.5386</td><td>94.6192</td><td>18923.8491</td><td>4840.8246</td><td>69.5760</td><td>409.1463</td><td>81829.2773</td><td>5.2410</td><td>2.2893</td><td>10.9729</td><td>2194.5960</td><td>7.4527</td><td>2.7299</td><td>13.0146</td><td>2602.9353</td><td>28.1291</td><td>5.3036</td><td>4.5530</td><td>910.6085</td><td>0.5467</td><td>0.7394</td><td>200</td>
  </tr>
  <tr bgcolor='#f6f6f6'>
    <td>2500</td>
    <td><strong>proto</strong></td>
    <td>2.7160</td><td>543.2126</td><td>27.7985</td><td>5.2724</td><td>46.3008</td><td>9260.1785</td><td>5218.2064</td><td>72.2371</td><td>64.2468</td><td>12849.3683</td><td>5401.4245</td><td>73.4943</td><td>196.6189</td><td>39323.7841</td><td>5.1478</td><td>2.2688</td><td>2.3345</td><td>466.9148</td><td>1.1116</td><td>1.0543</td><td>5.0506</td><td>1010.1275</td><td>28.1992</td><td>5.3102</td><td>3.4798</td><td>695.9631</td><td>0.5952</td><td>0.7715</td><td>200</td>
  </tr>
  <tr>
    <td>5000</td>
    <td><strong>json</strong></td>
    <td>21.2663</td><td>4253.2708</td><td>38.3800</td><td>6.1951</td><td>86.5728</td><td>17314.5668</td><td>807.9398</td><td>28.4242</td><td>129.9238</td><td>25984.7795</td><td>1101.6638</td><td>33.1913</td><td>818.2927</td><td>163658.5546</td><td>20.3879</td><td>4.5152</td><td>21.4515</td><td>4290.3180</td><td>37.4712</td><td>6.1213</td><td>42.7179</td><td>8543.5888</td><td>79.3336</td><td>8.9069</td><td>6.4189</td><td>1283.7804</td><td>1.2827</td><td>1.1325</td><td>200</td>
  </tr>
  <tr bgcolor='#f6f6f6'>
    <td>5000</td>
    <td><strong>proto</strong></td>
    <td>27.6636</td><td>5532.7289</td><td>66.4214</td><td>8.1499</td><td>53.2453</td><td>10649.0797</td><td>663.5768</td><td>25.7599</td><td>78.1782</td><td>15635.6418</td><td>765.3834</td><td>27.6655</td><td>393.2310</td><td>78646.2011</td><td>20.1829</td><td>4.4925</td><td>2.3413</td><td>468.2619</td><td>1.9777</td><td>1.4063</td><td>30.0049</td><td>6000.9908</td><td>68.3459</td><td>8.2671</td><td>5.2374</td><td>1047.4822</td><td>1.1018</td><td>1.0496</td><td>200</td>
  </tr>
  <tr>
    <td>7500</td>
    <td><strong>json</strong></td>
    <td>36.4672</td><td>7293.4467</td><td>74.4293</td><td>8.6272</td><td>109.1009</td><td>21820.1968</td><td>1296.5880</td><td>36.0081</td><td>170.7690</td><td>34153.8140</td><td>2116.5922</td><td>46.0064</td><td>1227.4391</td><td>245487.8320</td><td>37.3844</td><td>6.1142</td><td>35.5830</td><td>7116.6002</td><td>52.2269</td><td>7.2268</td><td>72.0502</td><td>14410.0470</td><td>150.7565</td><td>12.2782</td><td>7.4161</td><td>1483.2323</td><td>2.4694</td><td>1.5714</td><td>200</td>
  </tr>
  <tr bgcolor='#f6f6f6'>
    <td>7500</td>
    <td><strong>proto</strong></td>
    <td>42.8540</td><td>8570.8079</td><td>111.8343</td><td>10.5751</td><td>59.1027</td><td>11820.5561</td><td>425.5108</td><td>20.6279</td><td>91.9510</td><td>18390.2003</td><td>879.1169</td><td>29.6499</td><td>589.8430</td><td>117968.6181</td><td>39.1367</td><td>6.2559</td><td>3.1930</td><td>638.6041</td><td>8.9121</td><td>2.9853</td><td>46.0470</td><td>9209.4120</td><td>119.7761</td><td>10.9442</td><td>6.6794</td><td>1335.8862</td><td>2.1216</td><td>1.4566</td><td>200</td>
  </tr>
  <tr>
    <td>10000</td>
    <td><strong>json</strong></td>
    <td>48.6333</td><td>9726.6724</td><td>140.1636</td><td>11.8390</td><td>128.3987</td><td>25679.7518</td><td>1335.8527</td><td>36.5493</td><td>209.7768</td><td>41955.3730</td><td>2054.1530</td><td>45.3227</td><td>1636.5855</td><td>327317.1093</td><td>79.9775</td><td>8.9430</td><td>47.1698</td><td>9433.9718</td><td>44.9118</td><td>6.7016</td><td>95.8032</td><td>19160.6442</td><td>183.1097</td><td>13.5318</td><td>7.9045</td><td>1580.9102</td><td>1.9447</td><td>1.3945</td><td>200</td>
  </tr>
  <tr bgcolor='#f6f6f6'>
    <td>10000</td>
    <td><strong>proto</strong></td>
    <td>56.2058</td><td>11241.1789</td><td>128.7184</td><td>11.3454</td><td>77.2350</td><td>15447.0021</td><td>1091.4103</td><td>33.0365</td><td>118.5260</td><td>23705.2149</td><td>1395.0088</td><td>37.3498</td><td>786.4551</td><td>157291.0351</td><td>78.2986</td><td>8.8486</td><td>4.0583</td><td>811.6765</td><td>4.9254</td><td>2.2193</td><td>60.2642</td><td>12052.8554</td><td>138.2736</td><td>11.7589</td><td>6.9564</td><td>1391.2870</td><td>2.7061</td><td>1.6450</td><td>200</td>
  </tr>
</table>
